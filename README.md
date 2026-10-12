# Voice Assistant MVP

Proyecto mínimo en Python para crear un asistente con voz que:
1. escucha desde el micrófono,
2. transcribe con Whisper,
3. responde con GPT,
4. reproduce la respuesta con voz local, gTTS o ElevenLabs.

## Requisitos
- Python 3.8+
- Micrófono y altavoz
- API key de OpenAI
- (Opcional) API key de ElevenLabs para voz más natural
- ffmpeg para convertir archivos de audio (si usas MP3 u otros formatos)

## Instalación

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y agrega tus claves:

```env
OPENAI_API_KEY=tu_api_key_aqui
ELEVENLABS_API_KEY=tu_key_de_elevenlabs
ELEVEN_VOICE_ID=qO80WzLXn31Ps3Xf2V7d
TTS_PROVIDER=elevenlabs
```

Opciones válidas para `TTS_PROVIDER`:
- `elevenlabs`
- `pyttsx3`
- `gtts`

## Ejecutar con micrófono

```bash
python assistant_mvp_voice.py
```

Luego pulsa Enter para grabar voz. El asistente transcribirá lo que digas y te responderá con voz.

## Ejecutar con un archivo de audio

Si ya tienes un audio en formato WAV, puedes hacer:

```bash
python assistant_mvp_voice.py mi_voz.wav
```

Si el archivo es MP3 u otro formato, convírtelo primero a WAV con ffmpeg:

```bash
ffmpeg -i mi_voz.mp3 -ar 16000 -ac 1 mi_voz.wav
python assistant_mvp_voice.py mi_voz.wav
```

## Voz
- `TTS_PROVIDER=elevenlabs` usa ElevenLabs y la voz de `ELEVEN_VOICE_ID`.
- `TTS_PROVIDER=pyttsx3` usa la voz local del sistema.
- `TTS_PROVIDER=gtts` usa Google Text-to-Speech y genera audio con gTTS.

## Notas
- Este MVP usa Whisper + ChatGPT + voz local, gTTS o ElevenLabs.
- `pyttsx3` usa voz local del sistema y puede variar según el sistema operativo.
- El uso de OpenAI y ElevenLabs tiene costo según tu plan.
- Si tu micrófono o parlantes no funcionan, revisa la configuración del sistema.
