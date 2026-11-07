"""Trascrizione audio con speaker diarization via AssemblyAI."""
import os
import tempfile

import assemblyai as aai
import streamlit as st

st.set_page_config(page_title="Audio Transcriber", page_icon="🎙️", layout="centered")

LANGUAGES = {
    "Rilevamento automatico": None,
    "Italiano": "it",
    "English": "en",
    "Français": "fr",
    "Deutsch": "de",
    "Español": "es",
}


def get_api_key() -> str:
    """Priorità: secrets.toml > variabile d'ambiente > input manuale."""
    try:
        key = st.secrets.get("ASSEMBLYAI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("ASSEMBLYAI_API_KEY", "")


def fmt_ts(ms: int) -> str:
    s = ms // 1000
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


@st.cache_data(show_spinner=False)
def transcribe(audio_bytes: bytes, suffix: str, api_key: str, lang: str | None, speakers: int | None):
    aai.settings.api_key = api_key
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=speakers,
        language_code=lang,
        language_detection=lang is None,
        punctuate=True,
        format_text=True,
    )
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        path = f.name
    try:
        t = aai.Transcriber(config=config).transcribe(path)
    finally:
        os.unlink(path)
    if t.status == aai.TranscriptStatus.error:
        raise RuntimeError(t.error)
    return [(u.speaker, u.start, u.text) for u in (t.utterances or [])]


# --- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.header("Impostazioni")
    api_key = get_api_key() or st.text_input("AssemblyAI API key", type="password")
    lang_label = st.selectbox("Lingua", list(LANGUAGES))
    n_speakers = st.number_input("Numero speaker (0 = auto)", 0, 10, 0)

# --- Main --------------------------------------------------------------------
st.title("🎙️ Audio Transcriber")
st.caption("Carica un file audio: ottieni il transcript con l'indicazione degli speaker.")

audio = st.file_uploader(
    "File audio", type=["mp3", "wav", "m4a", "mp4", "ogg", "flac", "webm", "aac"]
)

if audio and st.button("Trascrivi", type="primary", disabled=not api_key):
    with st.spinner("Trascrizione in corso (circa 15-30% della durata dell'audio)…"):
        try:
            st.session_state.utterances = transcribe(
                audio.getvalue(),
                os.path.splitext(audio.name)[1],
                api_key,
                LANGUAGES[lang_label],
                n_speakers or None,
            )
            st.session_state.filename = os.path.splitext(audio.name)[0]
        except Exception as e:
            st.error(f"Errore: {e}")

if not api_key:
    st.info("Inserisci la API key AssemblyAI nella barra laterale.")

utterances = st.session_state.get("utterances")
if utterances:
    speakers = sorted({u[0] for u in utterances})
    with st.expander("✏️ Rinomina speaker", expanded=False):
        names = {s: st.text_input(f"Speaker {s}", value=f"Speaker {s}", key=f"sp_{s}") for s in speakers}

    lines = [f"[{fmt_ts(start)}] {names[sp]}: {text}" for sp, start, text in utterances]
    transcript = "\n\n".join(lines)

    st.subheader(f"Transcript · {len(speakers)} speaker")
    for sp, start, text in utterances:
        st.markdown(f"**{names[sp]}** · `{fmt_ts(start)}`  \n{text}")

    st.download_button(
        "⬇️ Scarica .txt",
        transcript,
        file_name=f"{st.session_state.filename}_transcript.txt",
        mime="text/plain",
    )
