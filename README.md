# Voice Assistant MVP

Proyecto mínimo en Python para crear un asistente con voz que:
1. escucha desde el micrófono,
2. transcribe con Whisper,
3. responde con GPT,
4. reproduce la respuesta con voz local o con ElevenLabs.

## Requisitos
- Python 3.8+
- Micrófono y altavoz
- API key de OpenAI
- (Opcional) API key de ElevenLabs para voz más natural
- ffmpeg para convertir archivos de audio (opcional, si usas MP3 u otros formatos)

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
```

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
- Si `ELEVENLABS_API_KEY` está presente, el proyecto usará ElevenLabs para generar audio.
- Si no está presente, usará `pyttsx3` como fallback local.

## Notas
- Este MVP usa Whisper + ChatGPT + voz local o ElevenLabs.
- `pyttsx3` usa voz local del sistema y puede variar según el sistema operativo.
- El uso de OpenAI y ElevenLabs tiene costo según tu plan.
- Si tu micrófono o parlantes no funcionan, revisa la configuración del sistema.
