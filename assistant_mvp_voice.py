#!/usr/bin/env python3
"""
MVP: escucha -> (Deepgram | Whisper) -> GPT -> voz (ElevenLabs, gTTS o pyttsx3)

Modo de uso:
- sin argumentos: graba desde el micrófono
- con un archivo: python assistant_mvp_voice.py mi_voz.wav
"""
import os
import sys
import subprocess
import tempfile
import time
import asyncio

import sounddevice as sd
import soundfile as sf
import pyttsx3
import requests
from dotenv import load_dotenv
import openai
from gtts import gTTS
from pydub import AudioSegment

# Deepgram SDK (optional)
try:
    from deepgram import Deepgram
except Exception:
    Deepgram = None

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

DEEPGRAM_KEY = os.getenv("DEEPGRAM_API_KEY")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs").lower()

SAMPLE_RATE = 16000
CHANNELS = 1
DEFAULT_DURATION = 5  # segundos por defecto


def record_to_wav(filename: str, duration: int):
    print(f"Grabando {duration} segundos... habla ahora.")
    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
    )
    sd.wait()
    sf.write(filename, recording, SAMPLE_RATE, subtype="PCM_16")
    print(f"Guardado en {filename}")


def convert_to_wav(input_path: str, output_path: str):
    """Convierte el audio a WAV mono 16kHz para transcripción.
    Requiere ffmpeg instalado en el sistema.
    """
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                str(CHANNELS),
                output_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg no está instalado. Instálalo y reintenta: https://www.ffmpeg.org/download.html"
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"No se pudo convertir el archivo de audio: {exc}")


def prepare_audio_for_whisper(audio_path: str) -> str:
    ext = os.path.splitext(audio_path.lower())[1]
    if ext == ".wav":
        return audio_path

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    convert_to_wav(audio_path, tmp_path)
    return tmp_path


# --- Transcripción: Deepgram (si está configurado) ---
async def _dg_transcribe_async(path: str, options: dict):
    if not Deepgram:
        raise RuntimeError("deepgram-sdk no está instalado. Añade 'deepgram-sdk' a requirements.txt y pip install -r requirements.txt")
    dg = Deepgram(DEEPGRAM_KEY)
    with open(path, "rb") as audio:
        audio_bytes = audio.read()
        source = {"buffer": audio_bytes, "mimetype": "audio/wav"}
        result = await dg.transcription.prerecorded(source, options)
    try:
        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
    except Exception:
        transcript = str(result)
    return transcript


def transcribe_with_deepgram(path: str) -> str:
    if not DEEPGRAM_KEY:
        raise RuntimeError("Falta DEEPGRAM_API_KEY en .env")
    print("Subiendo a Deepgram para transcripción...")
    options = {
        "punctuate": True,
        "language": "es",
    }
    try:
        text = asyncio.run(_dg_transcribe_async(path, options))
    except Exception as e:
        raise RuntimeError(f"Error al transcribir con Deepgram: {e}")
    print(f"Transcripción (Deepgram): {text}")
    return text


# --- Transcripción: Whisper (OpenAI) ---
def transcribe_with_whisper(path: str) -> str:
    if not OPENAI_KEY:
        raise RuntimeError("Falta OPENAI_API_KEY en .env")

    print("Subiendo a Whisper para transcripción...")
    with open(path, "rb") as audio_file:
        try:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            text = transcript["text"]
        except Exception as e:
            raise RuntimeError(f"Error al transcribir: {e}")
    print(f"Transcripción (Whisper): {text}")
    return text


# --- GPT ---
def ask_gpt(prompt: str) -> str:
    if not OPENAI_KEY:
        raise RuntimeError("Falta OPENAI_API_KEY en .env")

    print("Enviando a GPT...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente útil y conciso que responde en español.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.6,
    )
    text = response["choices"][0]["message"]["content"].strip()
    print(f"GPT: {text}")
    return text


# --- TTS providers ---
def speak_text_local(text: str):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for v in voices:
        try:
            lang = getattr(v, "languages", [""])[0]
        except IndexError:
            lang = ""
        if "spanish" in v.name.lower() or "es" in lang.lower():
            engine.setProperty("voice", v.id)
            break
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()


def speak_text_gtts(text: str):
    print("Usando gTTS...")
    mp3_path = "reply.mp3"
    wav_path = "reply.wav"

    tts = gTTS(text=text, lang="es", slow=False)
    tts.save(mp3_path)
    AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")

    data, samplerate = sf.read(wav_path, dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    sd.play(data, samplerate)
    sd.wait()

    if os.path.exists(mp3_path):
        os.remove(mp3_path)
    if os.path.exists(wav_path):
        os.remove(wav_path)


def speak_text_elevenlabs(text: str):
    eleven_key = os.getenv("ELEVENLABS_API_KEY")
    if not eleven_key:
        raise RuntimeError("Falta ELEVENLABS_API_KEY en .env")

    voice_id = os.getenv("ELEVEN_VOICE_ID", "qO80WzLXn31Ps3Xf2V7d")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": eleven_key,
        "Content-Type": "application/json",
        "Accept": "audio/wav",
    }

    payload = {
        "text": text,
        "model_id": "eleven_v4",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"ElevenLabs error {response.status_code}: {response.text}")

    output_path = "reply.wav"
    with open(output_path, "wb") as f:
        f.write(response.content)

    data, samplerate = sf.read(output_path, dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    sd.play(data, samplerate)
    sd.wait()


def speak_text(text: str):
    provider = TTS_PROVIDER
    if provider == "pyttsx3":
        speak_text_local(text)
        return

    if provider == "gtts":
        speak_text_gtts(text)
        return

    # provider es elevenlabs por defecto
    try:
        if os.getenv("ELEVENLABS_API_KEY") and provider == "elevenlabs":
            speak_text_elevenlabs(text)
            return
    except Exception as e:
        print(f"ElevenLabs falló: {e}. Usando voz local.")

    speak_text_local(text)


# --- Main flow ---
def main():
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"No existe el archivo: {audio_path}")

        print(f"Usando archivo de audio: {audio_path}")
        prepared_path = prepare_audio_for_whisper(audio_path)
        try:
            # Prioridad: Deepgram -> Whisper
            if DEEPGRAM_KEY:
                text = transcribe_with_deepgram(prepared_path)
            else:
                text = transcribe_with_whisper(prepared_path)

            if not text.strip():
                print("No se detectó voz en el archivo.")
                return
            reply = ask_gpt(text)
            speak_text(reply)
        finally:
            if prepared_path != audio_path and os.path.exists(prepared_path):
                os.unlink(prepared_path)
        return

    print("MVP asistente de voz — pulsa Enter para grabar (ctrl+c para salir).")
    filename = "input.wav"
    while True:
        try:
            raw = input(
                "\nEnter -> grabar (por defecto 5s). Si quieres otra duración escribe número de segundos y Enter:"
            )
            if raw.strip() == "":
                duration = DEFAULT_DURATION
            else:
                try:
                    duration = int(raw.strip())
                except ValueError:
                    print("Entrada no válida, usando duración por defecto.")
                    duration = DEFAULT_DURATION

            record_to_wav(filename, duration)

            # Prioridad: Deepgram -> Whisper
            if DEEPGRAM_KEY:
                text = transcribe_with_deepgram(filename)
            else:
                text = transcribe_with_whisper(filename)

            if not text.strip():
                print("No se detectó voz. Intenta de nuevo.")
                continue

            reply = ask_gpt(text)
            speak_text(reply)
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nSaliendo.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
