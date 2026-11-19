import streamlit as st


def inject_theme(dark_mode: bool = False, auth_page: bool = False) -> None:
    """Inject Transkribus-style parchment login or clean SaaS Documents workspace styling."""
    parchment_watermark_css = ""
    if auth_page:
        bg_main = "#F6F1E3"
        bg_sidebar = "#F9FAFB"
        text_primary = "#0F1E3D"
        accent_primary = "#142952"
        accent_hover = "#1E3A73"
        parchment_watermark_css = """
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
        .stApp {
            background-color: #F6F1E3 !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='420' viewBox='0 0 640 420'%3E%3Cg fill='%23C8B99A' fill-opacity='0.28' font-family='Noto Sans Devanagari, Georgia, serif'%3E%3Ctext x='24' y='55' font-size='22' transform='rotate(-4 24 55)'%3E%E0%A4%B9%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A4%B2%E0%A4%BF%E0%A4%96%E0%A4%BF%E0%A4%A4 %E0%A4%AA%E0%A4%BE%E0%A4%A0 %E0%A4%AA%E0%A4%B9%E0%A4%9A%E0%A4%BE%E0%A4%A8 %E0%A4%94%E0%A4%B0 %E0%A4%AD%E0%A4%BE%E0%A4%B7%E0%A4%BE%3C/text%3E%3Ctext x='330' y='90' font-size='20' font-style='italic' transform='rotate(3 330 90)'%3E%E0%A4%A6%E0%A5%87%E0%A4%B5%E0%A4%A8%E0%A4%BE%E0%A4%97%E0%A4%B0%E0%A5%80 %E0%A4%B2%E0%A4%BF%E0%A4%AA%E0%A4%BF %E0%A4%85%E0%A4%AD%E0%A4%BF%E0%A4%B2%E0%A5%87%E0%A4%96%3C/text%3E%3Ctext x='45' y='155' font-size='19' font-style='italic'%3E%E0%A4%B9%E0%A4%BF%E0%A4%82%E0%A4%A6%E0%A5%80 %E0%A4%8F%E0%A4%B5%E0%A4%82 %E0%A4%AE%E0%A4%B0%E0%A4%BE%E0%A4%A0%E0%A5%80 %E0%A4%B8%E0%A4%BE%E0%A4%B9%E0%A4%BF%E0%A4%A4%E0%A5%8D%E0%A4%AF %E0%A4%B8%E0%A4%82%E0%A4%97%E0%A5%8D%E0%A4%B0%E0%A4%B9%3C/text%3E%3Ctext x='360' y='210' font-size='23' transform='rotate(-2 360 210)'%3E%E0%A4%B6%E0%A4%AC%E0%A5%8D%E0%A4%A6 %E0%A4%B8%E0%A4%82%E0%A4%B0%E0%A4%9A%E0%A4%A8%E0%A4%BE %E0%A4%B5%E0%A4%BF%E0%A4%B6%E0%A5%8D%E0%A4%B2%E0%A5%87%E0%A4%B7%E0%A4%A3%3C/text%3E%3Ctext x='20' y='285' font-size='21' transform='rotate(2 20 285)'%3E%E0%A4%AE%E0%A4%B0%E0%A4%BE%E0%A4%A0%E0%A5%80 %E0%A4%86%E0%A4%A3%E0%A4%BF %E0%A4%B9%E0%A4%BF%E0%A4%82%E0%A4%A6%E0%A5%80 %E0%A4%B9%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A4%B2%E0%A5%87%E0%A4%96%E0%A4%A8%3C/text%3E%3Ctext x='310' y='355' font-size='20' font-style='italic'%3E%E0%A4%AA%E0%A4%BE%E0%A4%82%E0%A4%A1%E0%A5%81%E0%A4%B2%E0%A4%BF%E0%A4%AA%E0%A4%BF %E0%A4%A1%E0%A4%BF%E0%A4%9C%E0%A4%BF%E0%A4%9F%E0%A4%B2%E0%A5%80%E0%A4%95%E0%A4%B0%E0%A4%A3%3C/text%3E%3C/g%3E%3C/svg%3E") !important;
            background-repeat: repeat !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E0D5 !important;
            border-radius: 12px !important;
            box-shadow: 0 12px 34px rgba(20, 41, 82, 0.09) !important;
            padding: 1.4rem 1.75rem 1.6rem 1.75rem !important;
        }
        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }
        .stTextInput label p {
            color: #1E293B !important;
            font-weight: 600 !important;
            font-size: 0.86rem !important;
        }
        .stTextInput input {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 6px !important;
            padding: 0.55rem 0.75rem !important;
        }
        .stTextInput input:focus {
            border-color: #142952 !important;
            box-shadow: 0 0 0 2px rgba(20, 41, 82, 0.16) !important;
        }
        .stCheckbox label p {
            color: #334155 !important;
            font-size: 0.85rem !important;
        }
        """
    else:
        bg_main = "#FFFFFF"
        bg_sidebar = "#F9FAFB"
        text_primary = "#111827"
        accent_primary = "#3B5BDB"
        accent_hover = "#2F4AC2"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:wght@700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
        }}

        .stApp {{
            background-color: {bg_main} !important;
            color: {text_primary} !important;
        }}

        {parchment_watermark_css}

        /* Auth Screen Elements */
        .sb-auth-brand {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.65rem;
            margin-top: 0.35rem;
            margin-bottom: 1.25rem;
        }}
        .sb-auth-brand-title {{
            font-family: 'Merriweather', Georgia, serif;
            font-size: 2.05rem;
            font-weight: 700;
            color: #142952;
            letter-spacing: -0.02em;
        }}
        .sb-auth-heading {{
            font-size: 1.32rem;
            font-weight: 700;
            color: #111827;
            margin: 0 0 0.25rem 0;
        }}
        .sb-auth-sub {{
            font-size: 0.88rem;
            color: #6B7280;
            margin: 0 0 1rem 0;
        }}
        .sb-auth-footer {{
            text-align: center;
            color: #374151;
            font-size: 0.9rem;
            margin-top: 0.75rem;
            margin-bottom: 0.35rem;
        }}

        /* Clean Light Sidebar (Reference Style) */
        section[data-testid="stSidebar"] {{
            background-color: {bg_sidebar} !important;
            border-right: 1px solid #EAECF0 !important;
        }}
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {{
            color: #374151 !important;
        }}
        .sb-sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.48rem 0.85rem;
            background-color: #EEF2F6;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.9rem;
            color: #1F2937 !important;
            margin-bottom: 1rem;
        }}
        section[data-testid="stSidebar"] .stRadio label {{
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.92rem;
            transition: background 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stRadio label:hover {{
            background-color: #EEF2FF !important;
            color: #3B5BDB !important;
        }}
        section[data-testid="stSidebar"] button {{
            background-color: #FFFFFF !important;
            color: #1F2937 !important;
            border: 1px solid #D1D5DB !important;
        }}
        section[data-testid="stSidebar"] button p {{
            color: #1F2937 !important;
            font-weight: 600 !important;
        }}

        /* Workspace Page Header */
        .sb-page-title {{
            font-size: 1.65rem;
            font-weight: 700;
            color: #111827;
            letter-spacing: -0.02em;
            margin: 0 0 1rem 0;
        }}
        .sb-section-label {{
            font-size: 0.92rem;
            font-weight: 600;
            color: #1F2937;
            margin: 1.35rem 0 0.7rem 0;
        }}

        /* Folder Cards */
        .sb-folder-card {{
            background-color: #F4F5F7;
            border: 1px solid #ECEEF2;
            border-radius: 12px;
            padding: 1.1rem 1.2rem;
            transition: all 0.15s ease;
        }}
        .sb-folder-card:hover {{
            border-color: #C7D2FE;
            background-color: #EEF2FF;
        }}
        .sb-folder-title {{
            font-size: 0.94rem;
            font-weight: 600;
            color: #111827;
            margin-top: 0.65rem;
            margin-bottom: 0.2rem;
        }}
        .sb-folder-meta {{
            font-size: 0.78rem;
            color: #6B7280;
        }}

        /* Recent Document Horizontal Cards */
        .sb-recent-card {{
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 0.85rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.85rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
        }}
        .sb-file-icon-box {{
            width: 38px;
            height: 38px;
            border-radius: 8px;
            background-color: #F3F4F6;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .sb-recent-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 0.15rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .sb-recent-meta {{
            font-size: 0.76rem;
            color: #6B7280;
        }}

        /* All Files Table */
        .sb-table-wrap {{
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            overflow: hidden;
            background-color: #FFFFFF;
            width: 100%;
        }}
        .sb-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}
        .sb-table thead th {{
            background-color: #F9FAFB;
            color: #6B7280;
            font-weight: 600;
            font-size: 0.78rem;
            text-align: left;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #E5E7EB;
        }}
        .sb-table tbody td {{
            padding: 0.8rem 1rem;
            border-bottom: 1px solid #F3F4F6;
            color: #111827;
            vertical-align: middle;
        }}
        .sb-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        .sb-table tbody tr:hover {{
            background-color: #F9FAFB;
        }}
        .sb-badge-lang {{
            display: inline-block;
            padding: 0.18rem 0.65rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 600;
            background-color: #EEF2FF;
            color: #3B5BDB;
        }}
        .sb-user-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: #374151;
            font-size: 0.85rem;
        }}
        .sb-avatar {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background-color: #3B5BDB;
            color: #FFFFFF;
            font-size: 0.72rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        /* Stat & Output Boxes */
        .sb-stat {{
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
        }}
        .sb-stat-label {{
            color: #6B7280;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .sb-stat-value {{
            color: #111827;
            font-size: 1.32rem;
            font-weight: 700;
            margin-top: 0.18rem;
        }}
        .deva-box {{
            font-family: 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
            font-size: 1.2rem;
            line-height: 1.85;
            background-color: #F9FAFB;
            color: #111827;
            border: 1px solid #E5E7EB;
            border-left: 4px solid #3B5BDB;
            border-radius: 10px;
            padding: 1.1rem 1.25rem;
            white-space: pre-wrap;
            word-break: break-word;
        }}

        /* Primary Button (#142952 on Auth Page, Cobalt #3B5BDB in Workspace) */
        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button {{
            background-color: {accent_primary} !important;
            border: 1px solid {accent_primary} !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            padding: 0.48rem 1.05rem !important;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.12) !important;
        }}
        div.stButton > button[kind="primary"] p,
        div.stFormSubmitButton > button p {{
            color: #FFFFFF !important;
        }}
        div.stButton > button[kind="primary"]:hover,
        div.stFormSubmitButton > button:hover {{
            background-color: {accent_hover} !important;
            border-color: {accent_hover} !important;
        }}

        /* Secondary Buttons */
        div.stButton > button[kind="secondary"] {{
            background-color: #FFFFFF !important;
            border: 1px solid #D1D5DB !important;
            color: #374151 !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            padding: 0.45rem 0.95rem !important;
        }}
        div.stButton > button[kind="secondary"] p {{
            color: #374151 !important;
        }}
        div.stButton > button[kind="secondary"]:hover {{
            background-color: #F9FAFB !important;
            border-color: #9CA3AF !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )