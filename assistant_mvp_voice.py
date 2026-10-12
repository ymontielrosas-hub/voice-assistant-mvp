#!/usr/bin/env python3
"""
MVP: escucha -> Whisper (OpenAI) -> GPT -> pyttsx3 (voz)
Pulsa Enter para grabar (duración configurable).
"""
import os
import time
import sounddevice as sd
import soundfile as sf
import pyttsx3
from dotenv import load_dotenv
import openai

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("Pon OPENAI_API_KEY en .env")

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


def speak_text(text: str):
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
