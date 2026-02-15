<!--
Railway template metadata (reference for template editor — not displayed on GitHub)
title: Faster Whisper
description: Private Speech-to-Text and Text-to-Speech API via Speaches. Transcription + TTS with 52 voices. 4x Faster
tags: whisper, faster-whisper, speech-to-text, transcription, stt, asr, audio, audio-to-text, voice-recognition, subtitles, translation, ai, ai-tool, openai-compatible, speech-recognition, self-hosted, mcp, railway, template, deploy, tts, text-to-speech, voice-synthesis, kokoro, voice-generation, speech-synthesis, audio-generation
-->

# Deploy and Host Faster Whisper with Railway

**Turn any audio into text — or any text into speech. Private. Self-hosted. One click.**

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/nsBZGp?referralCode=Qf6zrX)

Your audio never leaves your server — unlike OpenAI, Google, or AssemblyAI. Includes Speech-to-Text transcription and Text-to-Speech with 52 natural voices. No servers to manage. No Docker knowledge needed. Ready in under 2 minutes.

---

## Your Data Stays Private

With cloud transcription services, every audio file is uploaded to someone else's servers. With this template, **your audio stays on your server**:

- **No data leaves your server** — audio is processed locally and never sent to any third party
- **No vendor training** — your audio is never used to improve someone else's AI
- **Compliance ready** — you control the infrastructure for GDPR, HIPAA, and data residency requirements

Ideal for: medical recordings, legal conversations, financial meetings, and anything you wouldn't want on someone else's servers.

---

## What You Get

- **Complete privacy** — audio processed on your server, never shared
- **Web interface** — upload audio in your browser, get text back instantly
- **Text-to-Speech** — type text, hear it spoken in 52 natural voices across 9 languages
- **OpenAI-compatible API** — drop-in replacement, works with existing tools
- **Subtitles** — generate SRT/VTT files for video
- **100+ languages** — transcribe and translate

---

## How It Works

1. **Click Deploy** — one click, everything is pre-configured
2. **Open your URL** — a login page guides you to your API key
3. **Sign in** — paste your key from the Railway Variables tab
4. **Transcribe or speak** — use the **Transcribe** tab to convert audio to text, or the **Text-to-Speech** tab to generate spoken audio from text

No coding required.

---

## Self-Hosted vs Cloud Transcription

| | **This Template** | **OpenAI Whisper API** | **Google Speech-to-Text** |
|---|---|---|---|
| **Data privacy** | Your server only | Uploaded to OpenAI | Uploaded to Google |
| **Data training** | Never | May be used per ToS | May be used per ToS |
| **Pricing** | ~$7-10/mo flat | $0.006/min (usage) | $0.006-0.009/min |
| **Setup time** | 2 minutes | API key signup | Console + billing |
| **API format** | OpenAI (drop-in) | OpenAI | Google |
| **Compliance** | You control it | Depends on DPA | Depends on DPA |

---

## What It Costs

| Model | Monthly Cost | Best For |
|---|---|---|
| **Tiny** | **~$7-10/mo** | Fastest startup, light use |
| **Base** (default) | ~$12-15/mo | Getting started, best speed/quality balance |
| **Small** | ~$18-22/mo | Better accuracy on noisy audio |
| **Medium** | ~$30-35/mo | Maximum accuracy |

**vs OpenAI:** Transcribing 30 min/day on OpenAI = ~$5.40/mo and scales with usage. This template is flat-rate — same cost for 1 minute or 1,000 minutes.

Railway Hobby plan required ($5/mo + usage). New users get a free trial. [See pricing](https://railway.com/pricing)

---

## Common Use Cases

- **Confidential transcription** — medical, legal, or financial recordings stay on your server
- **Video and podcast transcription** — searchable text in seconds
- **Subtitle generation** — SRT/VTT files for YouTube, social media, or video editors
- **Voice-to-text for apps** — add speech recognition via a simple API call
- **Meeting notes** — transcribe and keep recordings on your own infrastructure
- **AI agent audio processing** — give AI agents the ability to process voice inputs

---

<details>
<summary><strong>Quick Start Guide</strong> — detailed step-by-step setup</summary>

### Step 1: Deploy

Click **Deploy on Railway** above. Review the pre-configured settings (defaults work out of the box) and click **Deploy**. The first deploy downloads the AI model (~142 MB for the default `base` model) and takes about 1-2 minutes.

### Step 2: Open Your URL

Once deployed, go to your Railway project:

1. Click on the **Faster Whisper** service
2. Go to the **Settings** tab > **Networking** > find your **Public Domain** (e.g., `faster-whisper-production-xxxx.up.railway.app`)
3. Open the URL in your browser

### Step 3: Sign In

You'll see a login page that guides you to your API key:

1. Go to your Railway dashboard and click the **Faster Whisper** service
2. Go to the **Variables** tab > find **API_KEY**
3. Copy the key and paste it into the login page
4. Click **Sign in** — you're in!

Your key is saved in your browser, so you only need to do this once.

### Step 4: Transcribe or Speak

Upload an audio file in the **Transcribe** tab, or switch to **Text-to-Speech** to generate spoken audio from text.

### Step 5: Use the API (Optional)

For programmatic access, use the API with your domain and API key:

```bash
curl -X POST https://YOUR_DOMAIN/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@audio.mp3 \
  -F model=Systran/faster-whisper-base
```

Replace `YOUR_DOMAIN` with your Railway public domain and `YOUR_API_KEY` with the key from your service variables.

</details>

<details>
<summary><strong>Supported Audio Formats</strong></summary>

**mp3**, **mp4**, **mpeg**, **mpga**, **m4a**, **wav**, **webm**, **flac**, **ogg**

These cover most common formats including iPhone recordings (m4a), web audio (webm), and professional formats (wav, flac).

</details>

<details>
<summary><strong>API Reference</strong> — endpoints, examples, and Python code</summary>

All endpoints require authentication via the `Authorization: Bearer YOUR_API_KEY` header.

### Transcribe Audio

```bash
curl -X POST https://YOUR_DOMAIN/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@audio.mp3 \
  -F model=Systran/faster-whisper-base
```

Response:
```json
{"text": "Hello, welcome to our weekly team meeting."}
```

### Generate Subtitles (SRT)

```bash
curl -X POST https://YOUR_DOMAIN/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@video-audio.mp3 \
  -F model=Systran/faster-whisper-base \
  -F response_format=srt
```

Response:
```
1
00:00:00,000 --> 00:00:02,500
Hello, welcome to our weekly team meeting.
```

### Generate Subtitles (VTT)

```bash
curl -X POST https://YOUR_DOMAIN/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@video-audio.mp3 \
  -F model=Systran/faster-whisper-base \
  -F response_format=vtt
```

### Translate Audio to English

```bash
curl -X POST https://YOUR_DOMAIN/v1/audio/translations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@french-audio.mp3 \
  -F model=Systran/faster-whisper-base
```

### Specify Language for Better Accuracy

```bash
curl -X POST https://YOUR_DOMAIN/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@audio.mp3 \
  -F model=Systran/faster-whisper-base \
  -F language=en
```

Use [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes): `en` (English), `fr` (French), `de` (German), `es` (Spanish), `zh` (Chinese), `ja` (Japanese), etc.

### Response Formats

| Format | Parameter | Use Case |
|---|---|---|
| JSON (default) | `response_format=json` | Get transcribed text as JSON |
| Plain text | `response_format=text` | Get raw text without JSON wrapper |
| SRT subtitles | `response_format=srt` | Subtitle files for video editors |
| VTT subtitles | `response_format=vtt` | Web-standard subtitles for HTML5 video |
| Verbose JSON | `response_format=verbose_json` | Detailed output with timestamps and confidence |

### Text-to-Speech

```bash
curl -X POST https://YOUR_DOMAIN/v1/audio/speech \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, welcome to our meeting.", "model": "tts-1", "voice": "af_heart", "speed": 1.0, "response_format": "mp3"}' \
  --output speech.mp3
```

### Choose a Voice

| Language | Voices |
|---|---|
| American English (Female) | af_heart (default), af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky |
| American English (Male) | am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck, am_santa |
| British English (Female) | bf_alice, bf_emma, bf_isabella, bf_lily |
| British English (Male) | bm_daniel, bm_fable, bm_george, bm_lewis |
| Japanese | jf_alpha, jf_gongitsune, jf_nezumi, jf_tebukuro, jm_kumo |
| Chinese | zf_xiaobei, zf_xiaoni, zf_xiaoxiao, zf_xiaoyi, zm_yunjian, zm_yunxi, zm_yunxia, zm_yunyang |
| Spanish | ef_dora, em_alex, em_santa |
| French | ff_siwis |
| Hindi | hf_alpha, hf_beta, hm_omega, hm_psi |
| Italian | if_sara, im_nicola |
| Portuguese | pf_dora, pm_alex, pm_santa |

### Python Example (OpenAI Library)

Since the API is OpenAI-compatible, you can use the official OpenAI Python library:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://YOUR_DOMAIN/v1",
    api_key="YOUR_API_KEY"
)

# Transcribe
with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="Systran/faster-whisper-base",
        file=audio_file
    )
    print(transcript.text)

# Translate to English
with open("french-audio.mp3", "rb") as audio_file:
    translation = client.audio.translations.create(
        model="Systran/faster-whisper-base",
        file=audio_file
    )
    print(translation.text)
```

### Python TTS Example

```python
# Text-to-Speech
response = client.audio.speech.create(
    model="tts-1",
    voice="af_heart",
    input="Hello, welcome to our meeting.",
    response_format="mp3"
)
response.stream_to_file("speech.mp3")
```

Install: `pip install openai`

</details>

<details>
<summary><strong>Configuration</strong> — environment variables and settings</summary>

All settings are managed via Railway environment variables. Defaults are production-ready — you don't need to change anything for the template to work.

| Variable | Default | Description |
|---|---|---|
| `PRELOAD_MODELS` | `["Systran/faster-whisper-base", "speaches-ai/Kokoro-82M-v1.0-ONNX"]` | Models to download at startup |
| `WHISPER__COMPUTE_TYPE` | `int8` | Quantization: `int8` (recommended for CPU) or `float32` |
| `WHISPER__INFERENCE_DEVICE` | `cpu` | Inference device (CPU only on Railway) |
| `STT_MODEL_TTL` | `-1` | Seconds before unloading STT model from memory. `-1` = never unload |
| `TTS_MODEL_TTL` | `300` | Seconds before unloading TTS model from memory. `-1` = never unload |
| `ENABLE_UI` | `false` | Disabled — custom frontend serves the web interface |
| `API_KEY` | Auto-generated | API key for authentication. Protects all API endpoints |
| `ALLOW_ORIGINS` | `["*"]` | CORS allowed origins (JSON array). Change to your domain for production |
| `LOG_LEVEL` | `info` | Logging verbosity: `debug`, `info`, `warning`, `error` |

</details>

<details>
<summary><strong>Available Models</strong> — sizes, RAM requirements, and how to switch</summary>

All models work with CPU inference and INT8 quantization on Railway.

### Multilingual (100+ languages)

| Model | Download | RAM (INT8) | Speed | Quality |
|---|---|---|---|---|
| `Systran/faster-whisper-tiny` | 75 MB | ~512 MB | Fastest | Basic |
| `Systran/faster-whisper-base` | 142 MB | ~1 GB | Fast | Good |
| `Systran/faster-whisper-small` | 466 MB | ~1.5 GB | Moderate | Great |
| `Systran/faster-whisper-medium` | 1.5 GB | ~2.5 GB | Slow | Excellent |

### English Only (faster and more accurate for English)

| Model | Download | RAM (INT8) | Speed | Quality |
|---|---|---|---|---|
| `Systran/faster-whisper-tiny.en` | 75 MB | ~512 MB | Fastest | Basic |
| `Systran/faster-whisper-base.en` | 142 MB | ~1 GB | Fast | Good |
| `Systran/faster-whisper-small.en` | 466 MB | ~1.5 GB | Moderate | Great |
| `Systran/faster-whisper-medium.en` | 1.5 GB | ~2.5 GB | Slow | Excellent |

**Default:** `base` — the best balance of speed and accuracy for CPU. Transcribes at ~3.4x real-time. Upgrade to `small` or `medium` for better accuracy on noisy audio, or use `tiny` for fastest startup.

### Text-to-Speech Model

| Model | Download | Voices | Languages |
|---|---|---|---|
| `speaches-ai/Kokoro-82M-v1.0-ONNX` | ~150 MB | 52 voices | 9 languages |

This model is preloaded by default. It runs on CPU via ONNX Runtime. Speed: ~40 characters/second (a short paragraph takes 2-3 seconds).

### How to Change Your Model

1. Go to your Railway project and click on the **Faster Whisper** service
2. Click the **Variables** tab
3. Find `PRELOAD_MODELS` and change the value to your chosen model, e.g., `["Systran/faster-whisper-medium"]`
4. Railway will automatically redeploy with the new model
5. The new model downloads during startup (75 MB to 1.5 GB depending on size)

**Tip:** You only need one STT model at a time. `base` (the default) is the sweet spot for most users.

### GPU Support

This template runs on **CPU only**. Railway does not currently offer GPU instances. Larger models (`large-v2`, `large-v3`, `large-v3-turbo`) require a GPU and are not included.

</details>

<details>
<summary><strong>Frequently Asked Questions</strong></summary>

**Is my audio data private?**
Yes. Audio is uploaded to your own Railway server, processed locally, and never sent to any third party.

**How long does it take to deploy?**
About 2 minutes. Click deploy, Railway builds the container and downloads the AI model (~75 MB).

**Do I need to know Docker or DevOps?**
No. Click deploy, get a working URL with a web interface and API. That's it.

**How do I transcribe audio?**
Two ways: (1) Open your URL in a browser and upload a file. (2) Send audio to the API endpoint with your API key.

**What audio formats are supported?**
MP3, MP4, M4A, WAV, WEBM, FLAC, OGG, MPEG, and MPGA.

**How accurate is the transcription?**
Depends on the model. Tiny is good for clear speech. Small or medium are better for professional use. All support 100+ languages.

**Can I change the AI model after deploying?**
Yes. Change the `PRELOAD_MODELS` variable and Railway redeploys automatically.

**Is this GDPR/HIPAA compliant?**
You control where data is processed. Audio never leaves your server. Consult your compliance team for specific requirements.

**What happens if the service crashes?**
Auto-restart (up to 10 retries) with health monitoring. Model persists on volume, so restarts take ~5 seconds.

**How does this compare to OpenAI's API pricing?**
Flat ~$7-10/mo vs $0.006/minute. Self-hosting is cheaper above ~40 hours/month. The main advantage is privacy.

**Can I generate speech from text?**
Yes. Switch to the Text-to-Speech tab, type your text, choose a voice, and click Generate. You can also use the API endpoint.

**How many TTS voices are available?**
52 voices across 9 languages including English (US/UK), Japanese, Chinese, Spanish, French, Hindi, Italian, and Portuguese.

**Is TTS slow for long text?**
On CPU, TTS generates ~40 characters/second. Short paragraphs take 2-3 seconds. Very long text (1000+ characters) may take 30+ seconds.

</details>

<details>
<summary><strong>Troubleshooting</strong></summary>

**Service keeps restarting** — First deploy downloads the AI model (1-2 min). Health check retries are normal. If it persists, try the `tiny` model.

**Out of memory** — Downgrade to a smaller model. `tiny` works with ~512 MB RAM.

**API returns 401** — Check your `Authorization: Bearer YOUR_API_KEY` header. Find your key in the **Variables** tab.

**Slow transcription** — CPU-only inference. `base` processes at ~3.4x realtime (1 min file = ~18 sec). `tiny` is even faster.

**Permission errors** — Ensure `RAILWAY_RUN_UID=0` is set in your service variables (pre-configured in the template).

**TTS takes too long** — CPU generates ~40 chars/sec. Keep text under 500 characters for best experience. Very long text (full pages) can take minutes.

**TTS model not found** — Ensure `PRELOAD_MODELS` includes `speaches-ai/Kokoro-82M-v1.0-ONNX`. The model downloads on first use if not preloaded.

</details>

<details>
<summary><strong>Updates and Backups</strong></summary>

### Template Updates
When we update this template's GitHub repository, Railway notifies all users. You'll see an update notification and can apply it when ready.

### Image Auto Updates (Optional)
1. Go to service **Settings** > **Source** > **Configure Auto Updates**
2. Choose update preference and maintenance window

**Note:** Requires changing to a mutable tag like `latest-cpu`. The default pinned tag (`0.9.0-rc.3-cpu`) does not auto-update.

### Backups
The volume stores downloaded AI models — public files that re-download automatically. **Backups are not critical** for this template. To enable: service **Settings** > **Backups** > choose a schedule.

</details>

<details>
<summary><strong>Verified Sources and Dependencies</strong></summary>

This template uses only official, verified open-source software:

| Component | Source | Stars | License | Version |
|---|---|---|---|---|
| **Speaches** (server) | [speaches-ai/speaches](https://github.com/speaches-ai/speaches) | 2.9k | MIT | v0.9.0-rc.3 |
| **Faster Whisper** (engine) | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 20.9k | MIT | v1.2.1 |
| **CTranslate2** (runtime) | [OpenNMT/CTranslate2](https://github.com/OpenNMT/CTranslate2) | 3.5k | MIT | — |
| **Whisper models** | [Systran on HuggingFace](https://huggingface.co/Systran) | — | MIT | — |
| **Kokoro TTS** (voices) | [speaches-ai/Kokoro-82M-v1.0-ONNX](https://huggingface.co/speaches-ai/Kokoro-82M-v1.0-ONNX) | — | Apache 2.0 | v1.0 |

**Docker image:** [`ghcr.io/speaches-ai/speaches:0.9.0-rc.3-cpu`](https://github.com/speaches-ai/speaches/pkgs/container/speaches) — pinned for stability. Built by the Speaches project via GHCR from [public source code](https://github.com/speaches-ai/speaches/actions).

**Changelogs:** [Speaches](https://github.com/speaches-ai/speaches/releases) | [Faster Whisper](https://github.com/SYSTRAN/faster-whisper/releases)

### Architecture

Everything runs in a single container. No databases or external services needed. Includes both Speech-to-Text (Faster Whisper) and Text-to-Speech (Kokoro) engines.

- **Volume** — `/home/ubuntu/.cache/huggingface/hub` caches models (1 GB default)
- **Health check** — `/docs` endpoint (no auth required)
- **Restart policy** — `ON_FAILURE` with 10 retries
- **Build** — Metal (V3) environment

### Why Deploy Faster Whisper on Railway?

Railway handles your infrastructure so you don't have to. You get a private, production-ready speech-to-text API without managing servers, Docker, networking, or storage. Your audio data stays on your server, making it ideal for privacy-conscious teams.

By deploying on Railway, you're one step closer to a complete full-stack application. Host your servers, databases, AI agents, and more on Railway.

</details>

---

**Links:** [Speaches docs](https://speaches.ai/) | [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) | [Speaches source](https://github.com/speaches-ai/speaches) | [OpenAI Whisper](https://github.com/openai/whisper) | [Whisper models](https://huggingface.co/Systran) | [Railway docs](https://docs.railway.com/templates) | [Railway pricing](https://railway.com/pricing)

---

MIT — [LICENSE](LICENSE)
