from collections import Counter, defaultdict
from typing import Dict, List, Optional

import htr_data as D
import htr_translate as TR

_PUNCT_STRIP = ".,;:!?।॥\"'()[]{}«»-–—…"


def _clean_token(tok: str) -> str:
    return tok.strip(_PUNCT_STRIP)


def is_orthographically_suspect(word: str) -> bool:
    """True if a Devanagari token violates basic orthographic structure (e.g. leading matra, double matra)."""
    core = _clean_token(word)
    if not core:
        return False
    if TR._is_mark(core[0]):
        return True
    if any(TR._is_vowel_sign(a) and TR._is_vowel_sign(b) for a, b in zip(core, core[1:])):
        return True
    return False


class DevanagariCorrector:
    """
    Language-aware Devanagari word suggestion engine built strictly from the project's
    training manifest transcripts and character n-gram LM (no external/fake OCR models).
    """

    def __init__(self, manifest_df, lm=None):
        self.lm = lm
        self.vocab_by_lang: Dict[str, Counter] = defaultdict(Counter)
        self.all_vocab: Counter = Counter()

        if manifest_df is not None and not manifest_df.empty:
            train_df = manifest_df[manifest_df["split"] == "train"] if "split" in manifest_df.columns else manifest_df
            for row in train_df.itertuples(index=False):
                lang = str(getattr(row, "language", "Hindi"))
                text = str(getattr(row, "text", ""))
                for raw in text.split():
                    w = _clean_token(raw)
                    if len(w) >= 2 and not is_orthographically_suspect(w):
                        self.vocab_by_lang[lang][w] += 1
                        self.all_vocab[w] += 1

    def get_candidates(self, word: str, language: str = "Hindi", prev_word: str = "", top_k: int = 4) -> List[str]:
        core = _clean_token(word)
        if not core:
            return []

        lexicon = self.vocab_by_lang.get(language) or self.all_vocab
        if not lexicon:
            return []

        max_dist = 1 if len(core) <= 3 else (2 if len(core) <= 6 else 3)
        scored = []

        for cand, freq in lexicon.items():
            if cand == core:
                continue
            if abs(len(cand) - len(core)) > max_dist:
                continue
            dist = D.edit_distance(core, cand)
            if dist <= max_dist:
                lm_bonus = 0.0
                if self.lm is not None:
                    ctx = f"{prev_word} {cand}".strip()
                    lm_bonus = -TR.bits_per_char(ctx, self.lm) * 0.35
                score = (-dist * 3.0) + (min(freq, 50) * 0.05) + lm_bonus
                scored.append((score, cand))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [cand for _, cand in scored[:top_k]]

    def analyze_text(
        self,
        text: str,
        language: str = "Hindi",
        word_confidences: Optional[List[dict]] = None,
        conf_threshold: float = 0.72,
    ) -> List[dict]:
        """
        Inspect each word in `text` and return structured items for potentially misread words:
        - index: token position in text.split()
        - original: original token (with punctuation preserved)
        - clean: stripped Devanagari word
        - reasons: list of why it was flagged
        - confidence: CTC alignment confidence if available
        - suggestions: list of candidate replacements
        """
        tokens = text.split()
        conf_map = {}
        if word_confidences:
            for i, item in enumerate(word_confidences):
                conf_map[i] = float(item.get("confidence", 1.0))

        lexicon = self.vocab_by_lang.get(language) or self.all_vocab
        flagged = []

        for idx, tok in enumerate(tokens):
            core = _clean_token(tok)
            if not core:
                continue

            prefix = tok[: tok.find(core)]
            suffix = tok[tok.find(core) + len(core) :]
            prev_clean = _clean_token(tokens[idx - 1]) if idx > 0 else ""

            suspect_ortho = is_orthographically_suspect(core)
            conf = conf_map.get(idx, None)
            low_conf = conf is not None and conf < conf_threshold
            in_vocab = core in lexicon

            reasons = []
            if suspect_ortho:
                reasons.append("Invalid Devanagari vowel/matra sequence")
            if low_conf:
                reasons.append(f"Low CTC alignment confidence ({conf:.0%})")
            if not in_vocab and len(core) >= 2:
                reasons.append(f"Not found in {language} training vocabulary")

            if not reasons:
                continue

            raw_cands = self.get_candidates(core, language=language, prev_word=prev_clean, top_k=4)
            formatted_cands = [f"{prefix}{c}{suffix}" for c in raw_cands]

            if formatted_cands or suspect_ortho or low_conf:
                flagged.append(
                    {
                        "index": idx,
                        "original": tok,
                        "clean": core,
                        "reasons": reasons,
                        "confidence": conf,
                        "suggestions": formatted_cands,
                    }
                )

        return flagged