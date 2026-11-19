import io
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTR_APP_DIR = os.path.join(BASE_DIR, "htr_app")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if HTR_APP_DIR not in sys.path:
    sys.path.insert(0, HTR_APP_DIR)

from pipeline import Pipeline
from scriptbridge_ui.theme import inject_theme
from scriptbridge_ui.auth import render_auth_page, update_user_profile


# ---------------------------------------------------------------------------
# Supported NLLB-200 Target Languages (8 Languages)
# ---------------------------------------------------------------------------
TARGET_LANGUAGES = [
    "English",
    "Hindi",
    "Marathi",
    "Telugu",
    "Tamil",
    "Bengali",
    "Gujarati",
    "Kannada",
]


# ---------------------------------------------------------------------------
# Page Configuration & Session State
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ScriptBridge",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "page" not in st.session_state:
    st.session_state.page = "Documents"
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "selected_doc_id" not in st.session_state:
    st.session_state.selected_doc_id = None


# ---------------------------------------------------------------------------
# Gate Application Behind Transkribus-Style Login / Register Screen
# ---------------------------------------------------------------------------
if st.session_state.auth_user is None:
    inject_theme(auth_page=True)
    render_auth_page()
    st.stop()

inject_theme(dark_mode=False, auth_page=False)
current_user = st.session_state.auth_user
user_id = current_user.get("user_id", "default")
user_name = current_user.get("name", "Researcher")
user_initials = "".join(part[0].upper() for part in user_name.split()[:2]) or "U"
user_settings = current_user.get(
    "settings",
    {"default_target_lang": "English", "review_threshold": 80, "translation_beams": 1},
)


# ---------------------------------------------------------------------------
# Persistent Per-User Document History Helpers
# ---------------------------------------------------------------------------
def _history_path() -> str:
    out_dir = os.path.join(HTR_APP_DIR, "htr_outputs")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, f"history_{user_id}.json")


def load_user_docs() -> List[Dict[str, Any]]:
    path = _history_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_user_docs(docs: List[Dict[str, Any]]) -> None:
    path = _history_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Cached Pipeline Loader
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_pipeline() -> Pipeline:
    prev_cwd = os.getcwd()
    try:
        os.chdir(HTR_APP_DIR)
        return Pipeline(mock=False)
    finally:
        os.chdir(prev_cwd)


# ---------------------------------------------------------------------------
# Clean Light Sidebar (Matching Reference Layout + Settings)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="sb-sidebar-brand"><span>✍️</span><span>ScriptBridge</span></div>',
        unsafe_allow_html=True,
    )

    nav_options = ["Documents", "New Recognition", "Document Editor", "Settings"]
    selected_page = st.radio(
        "Navigation",
        options=nav_options,
        index=nav_options.index(st.session_state.page)
        if st.session_state.page in nav_options
        else 0,
        label_visibility="collapsed",
    )
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.divider()
    st.caption(f"Signed in as **{user_name}**")
    if st.button("Sign Out", use_container_width=True):
        st.session_state.auth_user = None
        st.session_state.current_result = None
        st.session_state.selected_doc_id = None
        st.session_state.page = "Documents"
        st.rerun()


# ---------------------------------------------------------------------------
# SVG Icons (Single-Line Strings so Markdown Never Renders Code Blocks)
# ---------------------------------------------------------------------------
FOLDER_SVG = '<svg width="34" height="28" viewBox="0 0 36 30" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 5C2 3.34315 3.34315 2 5 2H13.5L16.5 5.5H31C32.6569 5.5 34 6.84315 34 8.5V25C34 26.6569 32.6569 28 31 28H5C3.34315 28 2 26.6569 2 25V5Z" fill="#6884F4"/></svg>'
DOC_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4B5563" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>'


# ---------------------------------------------------------------------------
# View 1: Documents Dashboard (Folders + Recent + All Files)
# ---------------------------------------------------------------------------
def render_documents_dashboard() -> None:
    st.markdown('<div class="sb-page-title">Documents</div>', unsafe_allow_html=True)

    t_new, t_filter, t_sort, _ = st.columns([1.05, 1.45, 1.55, 3.5], gap="small")
    with t_new:
        if st.button("＋  New", type="primary", use_container_width=True):
            st.session_state.page = "New Recognition"
            st.rerun()
    with t_filter:
        lang_filter = st.selectbox(
            "Filter",
            options=["All Languages", "Hindi", "Marathi"],
            label_visibility="collapsed",
        )
    with t_sort:
        sort_order = st.selectbox(
            "Sort",
            options=["Sort By: Latest", "Sort By: Name"],
            label_visibility="collapsed",
        )

    docs = load_user_docs()
    threshold = float(user_settings.get("review_threshold", 80))
    hindi_docs = [d for d in docs if d.get("language", "").lower() == "hindi"]
    marathi_docs = [d for d in docs if d.get("language", "").lower() == "marathi"]
    review_docs = [d for d in docs if float(d.get("lang_conf_pct", 0)) < threshold]

    # Folders Row
    st.markdown('<div class="sb-section-label">Folders</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4, gap="medium")
    folders = [
        ("All Transcriptions", f"{len(docs)} Files · Hindi & Marathi"),
        ("Hindi Documents", f"{len(hindi_docs)} Files · Devanagari"),
        ("Marathi Documents", f"{len(marathi_docs)} Files · Devanagari"),
        ("Needs Review", f"{len(review_docs)} Files · Below {int(threshold)}%"),
    ]
    for col, (title, meta) in zip([f1, f2, f3, f4], folders):
        with col:
            st.markdown(
                f'<div class="sb-folder-card">{FOLDER_SVG}<div class="sb-folder-title">{title}</div><div class="sb-folder-meta">{meta}</div></div>',
                unsafe_allow_html=True,
            )

    # Apply Filter & Sort
    filtered_docs = list(docs)
    if lang_filter == "Hindi":
        filtered_docs = [d for d in filtered_docs if d.get("language", "").lower() == "hindi"]
    elif lang_filter == "Marathi":
        filtered_docs = [d for d in filtered_docs if d.get("language", "").lower() == "marathi"]

    if sort_order == "Sort By: Name":
        filtered_docs.sort(key=lambda x: x.get("filename", "").lower())
    else:
        filtered_docs = list(reversed(filtered_docs))

    # Recent Row
    st.markdown('<div class="sb-section-label">Recent</div>', unsafe_allow_html=True)
    if not filtered_docs:
        st.info("No documents processed yet. Click **+ New** above to upload and recognize a handwritten page.")
    else:
        recent_items = filtered_docs[:3]
        r_cols = st.columns(3, gap="medium")
        for col, item in zip(r_cols, recent_items):
            with col:
                st.markdown(
                    f'<div class="sb-recent-card"><div class="sb-file-icon-box">{DOC_SVG}</div><div style="min-width:0;"><div class="sb-recent-title">{item["filename"]}</div><div class="sb-recent-meta">{item["timestamp"]} &nbsp;·&nbsp; {item["language"]} ({item["lang_conf_pct"]:.0f}%)</div></div></div>',
                    unsafe_allow_html=True,
                )

    # All Files Table + Quick Open Selector
    st.markdown('<div class="sb-section-label">All Files</div>', unsafe_allow_html=True)
    if filtered_docs:
        rows_html = []
        for item in filtered_docs:
            rows_html.append(
                f'<tr><td><div style="display:flex;align-items:center;gap:0.65rem;"><div class="sb-file-icon-box" style="width:30px;height:30px;">{DOC_SVG}</div><span style="font-weight:500;">{item["filename"]}</span></div></td><td><span class="sb-badge-lang">{item["language"]}</span></td><td style="color:#4B5563;">{item["lang_conf_pct"]:.1f}% &nbsp;·&nbsp; {item["num_lines"]} lines</td><td><span class="sb-user-pill"><span class="sb-avatar">{user_initials}</span><span>{user_name}</span></span></td></tr>'
            )

        table_html = (
            '<div class="sb-table-wrap"><table class="sb-table"><thead><tr>'
            '<th>Name ↓</th><th>Detected Language</th><th>Metrics</th><th>Upload By ↓</th>'
            '</tr></thead><tbody>' + "".join(rows_html) + "</tbody></table></div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        open_col1, open_col2 = st.columns([3, 1])
        with open_col1:
            doc_choices = {
                f"{d['filename']} ({d['language']} · {d['timestamp']}) [#{d['id']}]": d["id"]
                for d in filtered_docs
            }
            chosen_label = st.selectbox(
                "Select a document to view, edit, or translate",
                options=list(doc_choices.keys()),
            )
        with open_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Open in Editor →", type="primary", use_container_width=True):
                st.session_state.selected_doc_id = doc_choices[chosen_label]
                st.session_state.page = "Document Editor"
                st.rerun()
    else:
        empty_table = (
            '<div class="sb-table-wrap"><table class="sb-table"><thead><tr>'
            '<th>Name ↓</th><th>Detected Language</th><th>Metrics</th><th>Upload By ↓</th>'
            '</tr></thead><tbody><tr><td colspan="4" style="text-align:center;color:#6B7280;padding:1.5rem;">'
            'Your recognized documents will appear here automatically.</td></tr></tbody></table></div>'
        )
        st.markdown(empty_table, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# View 2: New Recognition (Upload, Recognize, Save & Translate)
# ---------------------------------------------------------------------------
def render_new_recognition_page() -> None:
    top_left, top_right = st.columns([5, 1.2])
    with top_left:
        st.markdown('<div class="sb-page-title">New Document Recognition</div>', unsafe_allow_html=True)
    with top_right:
        if st.button("← Back to Documents", use_container_width=True):
            st.session_state.page = "Documents"
            st.rerun()

    uploaded_file = st.file_uploader(
        "Upload a handwritten Devanagari page (PNG, JPG, JPEG, TIF, BMP)",
        type=["png", "jpg", "jpeg", "tif", "tiff", "bmp"],
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        preview_col, action_col = st.columns([1.25, 1], gap="large")
        with preview_col:
            st.image(pil_img, caption=uploaded_file.name, use_container_width=True)

        with action_col:
            st.markdown("#### Run HTR & Language ID")
            st.write("Extracts handwritten text and identifies the Language (Hindi or Marathi).")
            if st.button("Recognize & Identify Language", type="primary", use_container_width=True):
                suffix = os.path.splitext(uploaded_file.name)[1] or ".png"
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(image_bytes)
                        tmp_path = tmp.name

                    with st.spinner("Recognizing handwritten lines..."):
                        pipe = get_pipeline()
                        prev_cwd = os.getcwd()
                        try:
                            os.chdir(HTR_APP_DIR)
                            raw_res: Dict[str, Any] = pipe.recognise(tmp_path)
                        finally:
                            os.chdir(prev_cwd)

                    recognized_text = str(raw_res.get("text", "")).strip()
                    lang_label = str(
                        raw_res.get("language")
                        or raw_res.get("lang")
                        or raw_res.get("detected_language")
                        or "Unknown"
                    )
                    lang_conf = float(
                        raw_res.get("lang_confidence")
                        or raw_res.get("language_confidence")
                        or raw_res.get("confidence")
                        or 0.0
                    )
                    lang_conf_pct = lang_conf * 100.0 if lang_conf <= 1.0 else lang_conf
                    line_count = int(
                        raw_res.get("num_lines")
                        or raw_res.get("lines_count")
                        or (len(recognized_text.splitlines()) if recognized_text else 0)
                    )

                    record = {
                        "id": uuid.uuid4().hex[:8],
                        "filename": uploaded_file.name,
                        "timestamp": datetime.now().strftime("%b %d, %Y · %H:%M"),
                        "text": recognized_text,
                        "language": lang_label,
                        "lang_conf_pct": lang_conf_pct,
                        "num_lines": line_count,
                        "translation": "",
                        "target_lang": user_settings.get("default_target_lang", "English"),
                    }
                    st.session_state.current_result = record
                    st.session_state.selected_doc_id = record["id"]

                    docs = load_user_docs()
                    docs.append(record)
                    save_user_docs(docs)
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)

    res = st.session_state.current_result
    if res:
        st.divider()
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f'<div class="sb-stat"><div class="sb-stat-label">Detected Language</div><div class="sb-stat-value">{res["language"]}</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="sb-stat"><div class="sb-stat-label">Language Confidence</div><div class="sb-stat-value">{res["lang_conf_pct"]:.1f}%</div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f'<div class="sb-stat"><div class="sb-stat-label">Lines Extracted</div><div class="sb-stat-value">{res["num_lines"]}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Extracted Devanagari Text")
        st.markdown(
            f'<div class="deva-box">{res["text"] if res["text"] else "No readable text detected."}</div>',
            unsafe_allow_html=True,
        )

        act1, act2 = st.columns(2)
        with act1:
            st.download_button(
                label="Download Recognized Text (.txt)",
                data=res["text"],
                file_name=f"{os.path.splitext(res['filename'])[0]}_recognized.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with act2:
            if st.button("Edit & Translate in Document Editor →", type="primary", use_container_width=True):
                st.session_state.selected_doc_id = res["id"]
                st.session_state.page = "Document Editor"
                st.rerun()


# ---------------------------------------------------------------------------
# View 3: Document Editor & NLLB-200 Translation (8 Target Languages)
# ---------------------------------------------------------------------------
def render_document_editor_page() -> None:
    st.markdown('<div class="sb-page-title">Document Editor & Translation</div>', unsafe_allow_html=True)
    docs = load_user_docs()
    if not docs:
        st.info("No saved documents yet. Upload a handwritten document first.")
        if st.button("＋ New Recognition", type="primary"):
            st.session_state.page = "New Recognition"
            st.rerun()
        return

    doc_map = {d["id"]: d for d in docs}
    selected_id = st.session_state.selected_doc_id
    if selected_id not in doc_map:
        selected_id = docs[-1]["id"]
        st.session_state.selected_doc_id = selected_id

    labels = {
        f"{d['filename']} ({d['language']} · {d['timestamp']}) [#{d['id']}]": d["id"]
        for d in reversed(docs)
    }
    label_values = list(labels.values())
    default_idx = label_values.index(selected_id) if selected_id in label_values else 0

    chosen = st.selectbox("Active Document", options=list(labels.keys()), index=default_idx)
    selected_id = labels[chosen]
    st.session_state.selected_doc_id = selected_id
    doc = doc_map[selected_id]

    st.caption(
        f"Detected Language: **{doc['language']}** ({doc['lang_conf_pct']:.1f}%)  ·  "
        f"Lines: **{doc['num_lines']}**  ·  Processed: **{doc['timestamp']}**"
    )

    col_edit, col_trans = st.columns(2, gap="large")
    with col_edit:
        st.markdown("#### Transcription (Editable)")
        edited_text = st.text_area(
            "Correct any characters below and save",
            value=doc.get("text", ""),
            height=260,
            label_visibility="collapsed",
        )
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Save Corrections", type="primary", use_container_width=True):
                doc["text"] = edited_text
                doc["num_lines"] = len(edited_text.splitlines()) if edited_text.strip() else 0
                save_user_docs(docs)
                st.success("Transcription updated.")
        with b2:
            st.download_button(
                "Download .txt",
                data=edited_text,
                file_name=f"{os.path.splitext(doc['filename'])[0]}_edited.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with col_trans:
        st.markdown("#### Translation to Target Languge")
        default_tgt = doc.get("target_lang") or user_settings.get("default_target_lang", "English")
        tgt_idx = TARGET_LANGUAGES.index(default_tgt) if default_tgt in TARGET_LANGUAGES else 0
        target_lang = st.selectbox("Target Language (8 Languages)", options=TARGET_LANGUAGES, index=tgt_idx)

        if st.button("Translate Document", type="primary", use_container_width=True):
            if not edited_text.strip():
                st.warning("No text to translate.")
            else:
                with st.spinner(f"Translating from {doc['language']} to {target_lang}..."):
                    pipe = get_pipeline()
                    beams = int(user_settings.get("translation_beams", 1))
                    prev_cwd = os.getcwd()
                    try:
                        os.chdir(HTR_APP_DIR)
                        tr_res = pipe.translate(
                            text=edited_text,
                            source_language=doc["language"],
                            target_language=target_lang,
                            beams=beams,
                        )
                    finally:
                        os.chdir(prev_cwd)

                    translated_out = str(
                        tr_res.get("translation")
                        or tr_res.get("translated_text")
                        or tr_res.get("text")
                        or ""
                    ).strip()
                    doc["translation"] = translated_out
                    doc["target_lang"] = target_lang
                    save_user_docs(docs)

        translated_display = doc.get("translation", "")
        st.markdown(
            f'<div class="deva-box" style="min-height:175px;">{translated_display or "Select any of the 8 target languages and click Translate Document."}</div>',
            unsafe_allow_html=True,
        )
        if translated_display:
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                f"Download Translation ({doc.get('target_lang', target_lang)}) .txt",
                data=translated_display,
                file_name=f"{os.path.splitext(doc['filename'])[0]}_{doc.get('target_lang', target_lang).lower()}.txt",
                mime="text/plain",
                use_container_width=True,
            )


# ---------------------------------------------------------------------------
# View 4: Settings Section
# ---------------------------------------------------------------------------
def render_settings_page() -> None:
    st.markdown('<div class="sb-page-title">Settings</div>', unsafe_allow_html=True)

    tab_profile, tab_pipeline, tab_data = st.tabs(
        ["Account Profile", "Recognition & Translation", "Data & Storage"]
    )

    with tab_profile:
        st.markdown("#### Profile Details")
        with st.form("profile_settings_form"):
            fn_val = st.text_input("First name", value=current_user.get("first_name", user_name.split()[0]))
            ln_val = st.text_input(
                "Last name",
                value=current_user.get("last_name", " ".join(user_name.split()[1:])),
            )
            st.text_input("Email (read-only)", value=current_user.get("email", ""), disabled=True)
            save_prof = st.form_submit_button("Save Profile", type="primary")

        if save_prof:
            updated = update_user_profile(
                current_user.get("email", ""), fn_val, ln_val, user_settings
            )
            if updated:
                st.session_state.auth_user = updated
                st.success("Profile updated successfully.")
                st.rerun()

    with tab_pipeline:
        st.markdown("#### Default Processing Preferences")
        with st.form("pipeline_settings_form"):
            curr_tgt = user_settings.get("default_target_lang", "English")
            new_tgt = st.selectbox(
                "Default Translation Target Language (8 Languages)",
                options=TARGET_LANGUAGES,
                index=TARGET_LANGUAGES.index(curr_tgt) if curr_tgt in TARGET_LANGUAGES else 0,
            )
            new_thresh = st.slider(
                "Low-Confidence Review Folder Threshold (%)",
                min_value=50,
                max_value=99,
                value=int(user_settings.get("review_threshold", 80)),
            )
            new_beams = st.selectbox(
                "NLLB-200 Beam Search Width (1 = Fast, 4 = Higher Quality)",
                options=[1, 2, 4],
                index=[1, 2, 4].index(int(user_settings.get("translation_beams", 1))),
            )
            save_pipe = st.form_submit_button("Save Preferences", type="primary")

        if save_pipe:
            new_settings = {
                "default_target_lang": new_tgt,
                "review_threshold": new_thresh,
                "translation_beams": new_beams,
            }
            updated = update_user_profile(
                current_user.get("email", ""),
                current_user.get("first_name", user_name.split()[0]),
                current_user.get("last_name", ""),
                new_settings,
            )
            if updated:
                st.session_state.auth_user = updated
                st.success("Pipeline preferences saved.")
                st.rerun()

    with tab_data:
        st.markdown("#### Document History & Cache")
        docs = load_user_docs()
        st.write(f"You currently have **{len(docs)}** saved transcription(s) stored in your workspace.")

        if docs:
            export_json = json.dumps(docs, ensure_ascii=False, indent=2)
            st.download_button(
                "Export All Document History (.json)",
                data=export_json,
                file_name=f"scriptbridge_history_{user_id}.json",
                mime="application/json",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear All Saved Documents"):
            save_user_docs([])
            st.session_state.current_result = None
            st.session_state.selected_doc_id = None
            st.success("All saved documents cleared.")
            st.rerun()


# ---------------------------------------------------------------------------
# Main Router
# ---------------------------------------------------------------------------
if st.session_state.page == "Documents":
    render_documents_dashboard()
elif st.session_state.page == "New Recognition":
    render_new_recognition_page()
elif st.session_state.page == "Document Editor":
    render_document_editor_page()
elif st.session_state.page == "Settings":
    render_settings_page()