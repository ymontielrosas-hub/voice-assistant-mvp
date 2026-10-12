# Voice Assistant MVP

Proyecto mínimo en Python para crear un asistente con voz que:
1. escucha desde el micrófono,
2. transcribe con Whisper,
3. responde con GPT,
4. reproduce la respuesta con voz local.

## Requisitos
- Python 3.8+
- Micrófono y altavoz
- API key de OpenAI

## Instalación

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y coloca tu clave:

```env
OPENAI_API_KEY=tu_api_key_aqui
```

## Ejecutar

```bash
python assistant_mvp_voice.py
```

Luego pulsa Enter para grabar voz. El asistente transcribirá lo que digas y te responderá con voz.

## Notas
- Usa Whisper + ChatGPT + pyttsx3.
- `pyttsx3` usa voz local del sistema, que puede variar según el sistema operativo.
- El uso de OpenAI tiene costo según tu plan.
- Si tu micrófono o parlantes no funcionan, revisa la configuración del sistema.
