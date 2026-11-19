import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class HistoryStore:
    """Persistent JSON storage for ScriptBridge recognition, correction, and translation records."""

    def __init__(self, storage_path: Path):
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> List[Dict]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_all(self, records: List[Dict]) -> None:
        self.path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_record(
        self,
        document_name: str,
        detected_language: str,
        language_confidence: float,
        original_text: str,
        corrected_text: str = "",
        translation_text: str = "",
        translation_target: str = "English",
        n_lines: int = 0,
        reliability: str = "UNKNOWN",
        decoder_used: str = "",
    ) -> Dict:
        records = self.load_all()
        entry = {
            "id": str(uuid.uuid4())[:8],
            "document_name": document_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "detected_language": detected_language,
            "language_confidence": round(float(language_confidence), 4),
            "original_text": original_text,
            "corrected_text": corrected_text or original_text,
            "translation_text": translation_text,
            "translation_target": translation_target,
            "n_lines": int(n_lines),
            "reliability": reliability,
            "decoder_used": decoder_used,
        }
        records.insert(0, entry)
        self._save_all(records)
        return entry

    def update_record(self, record_id: str, **updates) -> Optional[Dict]:
        records = self.load_all()
        updated = None
        for rec in records:
            if rec.get("id") == record_id:
                rec.update(updates)
                rec["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated = rec
                break
        if updated is not None:
            self._save_all(records)
        return updated

    def delete_record(self, record_id: str) -> None:
        records = [r for r in self.load_all() if r.get("id") != record_id]
        self._save_all(records)

    def clear_all(self) -> None:
        self._save_all([])