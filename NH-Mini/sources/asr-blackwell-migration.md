---
title: "ASR Pipeline Blackwell Migration Debug"
type: source
tags: [aria, asr, blackwell, pyannote, bug-report]
sources: [lifelog-asr-server.py, asr_pipeline.py]
updated: 2026-05-11
---

# ASR Pipeline Blackwell Migration Debug

**Data ingest**: 2026-05-11
**Pagine toccate**: [[stack-lifelog2]], [[compatibility-blackwell-asr]]

## Takeaway chiave (Error Log)

Durante la migrazione della pipeline ASR su PC 139 (Blackwell sm_120), sono stati riscontrati e risolti i seguenti blocchi critici:

### 1. Incompatibilità Torchaudio 2.11+
- **Errore**: `AttributeError: module 'torchaudio' has no attribute 'list_audio_backends'` e crash su `torchaudio.io`.
- **Causa**: Torchaudio 2.11 ha rimosso API legacy usate internamente da SpeechBrain/Pyannote.
- **Soluzione**: Implementato monkeypatching preventivo in `server.py` e sostituito `torchaudio.load` con `soundfile.read` per il caricamento audio.

### 2. Autenticazione Gated Models (Hugging Face)
- **Errore**: `Model.from_pretrained()` fallisce per i modelli gated (embedding wespeaker).
- **Causa**: Mancanza di `HF_TOKEN` e configurazione "Offline Mode" forzata.
- **Soluzione**: 
    - Inserito token nel file `.env`.
    - Installato `python-dotenv` nell'ambiente virtuale.
    - Implementato `huggingface_hub.login(token)` globale all'avvio.

### 3. Conflitto Offline Mode & Cache
- **Errore**: `OfflineModeIsEnabled`.
- **Causa**: La variabile `HF_HUB_OFFLINE=1` era impostata nell'ambiente Windows, bloccando il login anche se il token era presente.
- **Soluzione**: Forzata `os.environ["HF_HUB_OFFLINE"] = "0"` **prima** di importare i moduli HF.
- **Ottimizzazione**: Reindirizzata la cache in `data\assets\models\huggingface` tramite `HF_HOME`.

### 4. API Pyannote 4.0.1 (Breaking Changes)
- **Errore**: `'DiarizeOutput' object has no attribute 'itertracks'`.
- **Causa**: Pyannote 4.x restituisce un oggetto contenitore invece della vecchia `Annotation`.
- **Soluzione**: Accesso ai dati tramite `res.speaker_diarization`.

## Note di integrazione
- L'ambiente `lifelog-asr` richiede ora obbligatoriamente `python-dotenv` e `soundfile`.
- Il caricamento audio deve sempre passare per `soundfile` su Blackwell per evitare crash di `libtorchcodec`.
