import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import threading
import time
import queue

recognizer = sr.Recognizer()
engine = pyttsx3.init()
speech_queue = queue.Queue()

# Female voice
voices = engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

def speak(text):
    chat_log.insert(tk.END, f"Assistant: {text}\n")
    chat_log.see(tk.END)
    speech_queue.put(text)

def process_speech_queue():
    try:
        while not speech_queue.empty():
            msg = speech_queue.get_nowait()
            engine.say(msg)
            engine.runAndWait()
    except Exception as e:
        print(f"[Speech Error] {e}")
    finally:
        root.after(100, process_speech_queue)

def get_time():
    return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."

def get_joke():
    return "Why did the developer go broke? Because he used up all his cache!"

def get_weather():
    try:
        weather_raw = requests.get("https://wttr.in/?format=3").text
        lower = weather_raw.lower()
        if "sun" in lower:
            emoji = "☀️"
        elif "cloud" in lower:
            emoji = "☁️"
        elif "rain" in lower:
            emoji = "🌧️"
        elif "thunder" in lower:
            emoji = "⛈️"
        elif "snow" in lower:
            emoji = "❄️"
        else:
            emoji = "🌤️"
        return f"{emoji} Weather info: {weather_raw}"
    except:
        return "❌ Unable to fetch the weather currently."

def open_app(app_name):
    try:
        os.system(f"start {app_name}")
        speak(f"Opening {app_name}")
    except:
        speak(f"Couldn't open {app_name}")

def play_music():
    try:
        os.startfile("spotify")  # Works if Spotify is in PATH
        speak("Opening Spotify")
    except:
        speak("Couldn't open Spotify.")

def process_command(command):
    command = command.lower()
    if "time" in command:
        speak(get_time())
    elif "joke" in command:
        speak(get_joke())
    elif "weather" in command:
        speak(get_weather())
    elif "open google" in command:
        speak("Launching Google.")
        webbrowser.open("https://www.google.com")
    elif "how are you" in command:
        speak("I'm fantastic and ready to assist!")
    elif "notepad" in command:
        open_app("notepad")
    elif "calculator" in command:
        open_app("calc")
    elif "play music" in command:
        play_music()
    elif "exit" in command or "quit" in command:
        speak("Goodbye! Talk to you later.")
        root.quit()
    else:
        speak("Sorry, I didn't get that.")

def listen_continuously():
    global last_interaction
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
    while True:
        with sr.Microphone() as source:
            mic_indicator.config(text="🎤 Listening...", fg=theme_fg["mic_active"])
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio)
                chat_log.insert(tk.END, f"You said: {command}\n")
                chat_log.see(tk.END)
                process_command(command)
                last_interaction = time.time()
            except sr.WaitTimeoutError:
                speak("You were silent. Please try again.")
            except sr.UnknownValueError:
                speak("I couldn't understand that.")
            except sr.RequestError:
                speak("Network issue.")
            finally:
                mic_indicator.config(text="🔈 Idle", fg=theme_fg["mic_idle"])
        time.sleep(1)

def idle_tips():
    global last_interaction
    tips = [
        "💡 Say: 'What's the weather like?'",
        "💡 Ask: 'Tell me a joke'",
        "💡 Try: 'What time is it?'",
        "💡 Ask: 'Open Google'",
        "💡 Say: 'Open Notepad'"
    ]
    i = 0
    while True:
        if time.time() - last_interaction > 30:
            speak(tips[i % len(tips)])
            i += 1
            last_interaction = time.time()
        time.sleep(10)

def toggle_theme():
    global current_theme
    if current_theme == "light":
        apply_dark_theme()
    else:
        apply_light_theme()

def apply_light_theme():
    global current_theme, theme_fg
    root.configure(bg="#ECF0F1")
    title.config(bg="#ECF0F1", fg="#2C3E50")
    chat_log.config(bg="#FDFEFE", fg="black")
    floating_tip.config(bg="#D6EAF8", fg="#154360")
    mic_indicator.config(fg="#95A5A6", bg="#ECF0F1")
    current_theme = "light"
    theme_fg["mic_idle"] = "#95A5A6"
    theme_fg["mic_active"] = "#E74C3C"

def apply_dark_theme():
    global current_theme, theme_fg
    root.configure(bg="#2C3E50")
    title.config(bg="#2C3E50", fg="white")
    chat_log.config(bg="#1C2833", fg="#ECF0F1")
    floating_tip.config(bg="#5D6D7E", fg="#F7F9F9")
    mic_indicator.config(fg="#ABB2B9", bg="#2C3E50")
    current_theme = "dark"
    theme_fg["mic_idle"] = "#ABB2B9"
    theme_fg["mic_active"] = "#F39C12"

def show_help():
    messagebox.showinfo("Commands", "You can try saying:\n\n"
                        "🕒 What's the time\n"
                        "😂 Tell me a joke\n"
                        "☁️ What's the weather\n"
                        "🌐 Open Google\n"
                        "📝 Open Notepad\n"
                        "🎵 Play Music\n"
                        "❓ How are you\n"
                        "🚪 Exit")

# GUI Setup
root = tk.Tk()
root.title("Smart Voice Assistant")
root.geometry("600x520")
# root.iconbitmap("assistant.ico")  # optional icon path

theme_fg = {"mic_idle": "#95A5A6", "mic_active": "#E74C3C"}
current_theme = "light"

title = tk.Label(root, text="🎙️ My Smart Assistant", font=("Helvetica", 18, "bold"))
title.pack(pady=10)

mic_indicator = tk.Label(root, text="🔈 Idle", font=("Helvetica", 12, "italic"))
mic_indicator.pack()

floating_tip = tk.Label(root, text="💬 Just speak anytime... I'm listening!",
                        font=("Segoe UI", 11, "italic"),
                        padx=10, pady=5, wraplength=450, justify="center")
floating_tip.pack(pady=5)

chat_log = scrolledtext.ScrolledText(root, font=("Segoe UI", 12), wrap=tk.WORD,
                                     width=66, height=15)
chat_log.pack(padx=10, pady=10)
chat_log.insert(tk.END, "Assistant: 👋 Hello! I'm your smart voice companion. Just speak, and I’ll handle the rest.\n\n")

# Bottom bar
bottom_bar = tk.Frame(root)
bottom_bar.pack(pady=5)

theme_btn = tk.Button(bottom_bar, text="🌓 Toggle Theme", command=toggle_theme)
theme_btn.grid(row=0, column=0, padx=10)

help_btn = tk.Button(bottom_bar, text="🛈 Help", command=show_help)
help_btn.grid(row=0, column=1, padx=10)

# Theme Setup
apply_light_theme()
last_interaction = time.time()

# Threads
threading.Thread(target=listen_continuously, daemon=True).start()
threading.Thread(target=idle_tips, daemon=True).start()
root.after(100, process_speech_queue)
root.mainloop()
