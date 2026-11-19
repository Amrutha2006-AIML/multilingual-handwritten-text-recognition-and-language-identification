# Handwritten Text Recognition and Language Identification (ScriptBridge)

An end-to-end deep learning system and interactive web application for **Devanagari Handwritten Text Recognition (HTR)**, **Language Identification** (Hindi, Marathi, Nepali), **Post-OCR Text Cleanup**, and **Neural Machine Translation** using Meta's **NLLB-600M**.

---

## Key Features
- **Multi-Architecture HTR Models:** Trained and compared **CNN**, **TCN**, and **Transformer** architectures with **CTC loss** and **Beam Search decoding**.
- **Language Identification:** Identifies script/language variations across **Hindi**, **Marathi**, and **Nepali** handwritten sentences.
- **Post-OCR Text Cleanup:** Automatically cleans noisy character extraction errors before downstream processing.
- **Multilingual Translation:** Integrates **NLLB-600M** (`htr_translate.py`) to translate recognized Devanagari text.
- **Interactive Web Interface:** Built with **Streamlit** (`scriptbridge_app.py` + `scriptbridge_ui/`) featuring authentication, theme customization, correction tools, and recognition history.

---

## Project Structure

```text
Capstone Project/
├── scriptbridge_app.py                  # Main Streamlit web application
├── scriptbridge_ui/                     # UI modules (auth, theme, storage, corrector)
├── htr_data.py                          # Dataset loading and image preprocessing
├── htr_torch.py                         # PyTorch model architectures & inference
├── htr_translate.py                     # NLLB-600M translation module
├── pipeline.py                          # End-to-end HTR + Language ID + Translation pipeline
├── 00_data_preparation.ipynb            # Dataset exploration & preprocessing
├── 01_cnn.ipynb                         # CNN model training & evaluation
├── 02_tcn.ipynb                         # TCN model training & evaluation
├── 03_transformer.ipynb                 # Transformer model training & evaluation
├── 04_compare_and_decoding.ipynb        # Model comparison & CTC/Beam Search decoding
├── 05_language_id_and_full_pipeline.ipynb # Language identification & integrated pipeline
├── 06_translation_NLLB_corrected.ipynb  # Post-OCR cleanup & NLLB translation workflow
├── requirements.txt                     # Core Python dependencies
├── requirements_translation.txt         # Translation model dependencies
└── .gitignore                           # Excludes datasets, caches, weights, and local logs