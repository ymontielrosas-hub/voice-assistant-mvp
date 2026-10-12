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

## Instalación

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y agrega tus claves:

```env
OPENAI_API_KEY=tu_api_key_aqui
ELEVENLABS_API_KEY=tu_key_de_elevenlabs
ELEVEN_VOICE_ID=Nh2zY9kknu6z4pZy6FhD
```

## Ejecutar

```bash
python assistant_mvp_voice.py
```

Luego pulsa Enter para grabar voz. El asistente transcribirá lo que digas y te responderá con voz.

## Voz
- Si `ELEVENLABS_API_KEY` está presente, el proyecto usará ElevenLabs para generar audio.
- Si no está presente, usará `pyttsx3` como fallback local.

## Notas
- Este MVP usa Whisper + ChatGPT + voz local o ElevenLabs.
- `pyttsx3` usa voz local del sistema y puede variar según el sistema operativo.
- El uso de OpenAI y ElevenLabs tiene costo según tu plan.
- Si tu micrófono o parlantes no funcionan, revisa la configuración del sistema.
