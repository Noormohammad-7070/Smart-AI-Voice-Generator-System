import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import threading
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ================= INITIALIZE TTS ENGINE GLOBALLY =================
# Initializing outside the function prevents "engine already started" errors
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

# ================= WINDOW =================
root = tk.Tk()
root.title("AI Voice Translator")
root.geometry("8000x650") # Note: Fixed your geometry from 8000 to 800 if needed
root.geometry("800x650")
root.configure(bg="#1e1e2f")
root.resizable(False, False)

# ================= TITLE =================
title = tk.Label(root, text="🌍 AI Voice Translator", font=("Helvetica", 22, "bold"),
                 bg="#1e1e2f", fg="#00ffcc")
title.pack(pady=20)

main_frame = tk.Frame(root, bg="#2b2b3c", bd=3, relief="ridge")
main_frame.pack(padx=20, pady=10, fill="both", expand=True)

# ================= LANGUAGE =================
languages = {"English": "en", "Hindi": "hi", "Telugu": "te", "Urdu": "ur", "Arabic": "ar"}
selected_lang = tk.StringVar()

tk.Label(main_frame, text="Select Target Language:", font=("Arial", 12),
         bg="#2b2b3c", fg="white").pack(pady=5)

lang_dropdown = ttk.Combobox(main_frame, textvariable=selected_lang,
                             values=list(languages.keys()), state="readonly", width=20)
lang_dropdown.pack()
lang_dropdown.current(0)

# ================= TEXT AREAS =================
tk.Label(main_frame, text="🎤 Input Speech:", font=("Arial", 12, "bold"),
         bg="#2b2b3c", fg="#00ffff").pack(pady=10)

input_text = tk.Text(main_frame, height=5, width=70, font=("Arial", 11),
                     bg="#3c3f58", fg="white", insertbackground="white")
input_text.pack()

tk.Label(main_frame, text="📝 Translated Output:", font=("Arial", 12, "bold"),
         bg="#2b2b3c", fg="#00ffff").pack(pady=10)

output_text = tk.Text(main_frame, height=5, width=70, font=("Arial", 11),
                      bg="#3c3f58", fg="white", insertbackground="white")
output_text.pack()

# ================= TOOLS =================
recognizer = sr.Recognizer()
translator = Translator()

# ================= FUNCTIONS =================

def update_status(message):
    status_label.config(text=message)

def listen():
    try:
        with sr.Microphone() as source:
            update_status("Adjusting for noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            update_status("Listening...")
            audio = recognizer.listen(source, timeout=5)
            update_status("Recognizing...")
            text = recognizer.recognize_google(audio)
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, text)
            update_status("Speech Captured")
    except Exception as e:
        update_status("Error: Mic not found or timeout")

def translate_text():
    try:
        text = input_text.get("1.0", tk.END).strip()
        if not text:
            update_status("Empty input!")
            return
        update_status("Translating...")
        lang_code = languages[selected_lang.get()]
        translated = translator.translate(text, dest=lang_code)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, translated.text)
        update_status("Translation Completed")
    except Exception as e:
        update_status("Translation Error")

# FIXED SPEAK FUNCTION
def speak_action():
    text = output_text.get("1.0", tk.END).strip()
    if not text:
        return
    
    def run_speech():
        try:
            update_status("Speaking...")
            # We recreate a local engine instance inside the thread 
            # for maximum stability with pyttsx3
            local_engine = pyttsx3.init()
            local_engine.say(text)
            local_engine.runAndWait()
            # Clean up after speaking
            local_engine.stop()
            update_status("Done Speaking")
        except Exception as e:
            print(f"TTS Error: {e}")
            update_status("Ready")

    # Run in a separate thread so the GUI doesn't freeze
    threading.Thread(target=run_speech, daemon=True).start()

def save_pdf():
    try:
        if not os.path.exists("output"): os.makedirs("output")
        text = output_text.get("1.0", tk.END).strip()
        if not text: return
        doc = SimpleDocTemplate("output/translation.pdf")
        styles = getSampleStyleSheet()
        elements = [Paragraph(text, styles["Normal"])]
        doc.build(elements)
        messagebox.showinfo("Saved", "PDF saved in output folder!")
    except Exception as e:
        messagebox.showerror("Error", "Could not save PDF. (Check for special characters)")

# ================= BUTTONS =================
button_frame = tk.Frame(main_frame, bg="#2b2b3c")
button_frame.pack(pady=20)

btn_style = {"font": ("Arial", 11, "bold"), "width": 12, "fg": "white"}

tk.Button(button_frame, text="🎤 Listen", command=lambda: threading.Thread(target=listen).start(),
          bg="#007acc", **btn_style).pack(side="left", padx=5)

tk.Button(button_frame, text="🌍 Translate", command=lambda: threading.Thread(target=translate_text).start(),
          bg="#28a745", **btn_style).pack(side="left", padx=5)

tk.Button(button_frame, text="🔊 Speak", command=speak_action,
          bg="#ff9800", **btn_style).pack(side="left", padx=5)

tk.Button(button_frame, text="💾 Save PDF", command=save_pdf,
          bg="#6f42c1", **btn_style).pack(side="left", padx=5)

status_label = tk.Label(root, text="Ready", bg="#141421", fg="#00ffcc", font=("Arial", 10))
status_label.pack(fill="x")

root.mainloop()