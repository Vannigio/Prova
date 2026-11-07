# Audio Transcriber (AssemblyAI)

App Streamlit: carichi un file audio e ottieni il transcript con **speaker diarization** (Speaker A, B, …), timestamp ed export `.txt`.

## Avvio rapido
```bash
cd transcriber
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ASSEMBLYAI_API_KEY="la-tua-api-key"   # oppure inseriscila nella sidebar
streamlit run app.py
```
In alternativa copia `.streamlit/secrets.toml.example` in `.streamlit/secrets.toml` (escluso da git).

## Funzioni
- Formati: mp3, wav, m4a, mp4, ogg, flac, webm, aac
- Lingua: auto-detect o forzata (IT/EN/FR/DE/ES)
- Numero speaker: automatico o indicato (migliora l'accuratezza se noto)
- Rinomina speaker (A → "Mario Rossi") prima dell'export
- Risultato in cache: cambiare i nomi non ri-chiama l'API (nessun costo extra)
