#!/usr/bin/env python3
"""
MVP: escucha -> Whisper (OpenAI) -> GPT -> voz (ElevenLabs o pyttsx3)
Pulsa Enter para grabar (duración configurable).
"""
import os
import time

import sounddevice as sd
import soundfile as sf
import pyttsx3
import requests
from dotenv import load_dotenv
import openai

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

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
    print(f"Transcripción: {text}")
    return text


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


def speak_text_elevenlabs(text: str):
    eleven_key = os.getenv("ELEVENLABS_API_KEY")
    if not eleven_key:
        raise RuntimeError("Falta ELEVENLABS_API_KEY en .env")

    voice_id = os.getenv("ELEVEN_VOICE_ID", "Nh2zY9kknu6z4pZy6FhD")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": eleven_key,
        "Content-Type": "application/json",
        "Accept": "audio/wav",
    }

    payload = {
        "text": text,
        "model_id": "eleven_v4",
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
    try:
        if os.getenv("ELEVENLABS_API_KEY"):
            speak_text_elevenlabs(text)
            return
    except Exception as e:
        print(f"ElevenLabs falló: {e}.Usando voz local.")

    speak_text_local(text)


def main():
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
