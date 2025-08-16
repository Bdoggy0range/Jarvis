import speech_recognition as sr
import webbrowser
import time
import os
import subprocess
import obswebsocket
import keyboard
import tkinter as tk
import threading
import queue
import sys

# OBS WebSocket connection details
OBS_HOST = "127.0.0.1"
OBS_PORT = 4444
OBS_PASSWORD = "password"  # Change this to your OBS WebSocket password

# Thread-safe queue for GUI updates
gui_queue = queue.Queue()

def reply(text):
    """Send text to the GUI queue for display."""
    gui_queue.put(text)

class JarvisGUI:
    """Simple Tkinter GUI for displaying assistant responses."""
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Jarvis")
        self.root.attributes("-topmost", True)
        self.root.geometry("300x100+1600+50")
        self.root.configure(bg="black")
        self.root.overrideredirect(True)
        self.label = tk.Label(
            self.root,
            text="Starting...",
            fg="lime",
            bg="black",
            font=("Consolas", 12)
        )
        self.label.pack(padx=10, pady=10)
        self.update_gui()

    def update_gui(self):
        """Update the GUI label with new text from the queue."""
        try:
            while True:
                text = self.queue.get_nowait()
                self.label.config(text=text)
                print(text)
        except queue.Empty:
            pass
        self.root.after(100, self.update_gui)

def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def log():
    """Log Jarvis startup time."""
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Jarvis started\n")

def clip():
    """Connect to OBS and record a 10-second clip."""
    client = obswebsocket.obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    try:
        client.connect()
        reply("Connected to OBS Successfully..")

        client.call(obswebsocket.requests.StartRecording())
        reply("Recording Started...")

        time.sleep(10)

        client.call(obswebsocket.requests.StopRecording())
        reply("Recording Stopped...")

    except Exception as e:
        reply(f"Error: {e}")

    finally:
        try:
            client.disconnect()
            reply("Disconnected from OBS")
        except Exception:
            pass

def listen(recognizer, prompt="Listening..."):
    """Listen for voice input and return recognized text."""
    reply(prompt)
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        return recognizer.recognize_google(audio).lower()

def launch_program(path):
    """Launch an external program."""
    try:
        subprocess.Popen(path, shell=True)
    except Exception as e:
        reply(f"Failed to launch: {e}")

def voice_loop():
    """Main loop for voice command recognition and execution."""
    recognizer = sr.Recognizer()
    clear()
    reply("Jarvis is starting...\nHold 'T' to talk.")

    waiting_for_followup = False
    active_personality = None

    # Define personalities and their commands
    personalities = {
        "jarvis": {
            "aliases": ["hey jarvis", "jarvis"],
            "commands": {
                ("clip that",): lambda: (clear(), clip()),
                ("quit",): lambda: "quit",
            }
        },
        "ultron": {
            "aliases": ["ultron", "hey ultron"],
            "commands": {
                ("scan my network",): lambda: (clear(), reply("Scanning your network..."), os.system("netstat")),
                ("quit",): lambda: "quit",
            }
        },
        "herbie": {
            "aliases": ["herbie", "hey herbie", "ain't that fantastic"],
            "commands": {
                ("play my jam",): lambda: (clear(), reply("Playing your jam..."), webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")),
                ("get fantastic",): lambda: (clear(), reply("Getting Fantastic..."), webbrowser.open("https://www.youtube.com/watch?v=_0yhnFeoFhA")),
                ("quit",): lambda: "quit",
            }
        },
    }

    def find_personality(command):
        """Return personality name if command matches an alias."""
        for name, data in personalities.items():
            if command in data["aliases"]:
                return name
        return None

    while True:
        try:
            if keyboard.is_pressed("t"):
                try:
                    command = listen(recognizer)

                    if not waiting_for_followup:
                        personality = find_personality(command)
                        if personality:
                            clear()
                            reply({
                                "jarvis": "Hello, Jarvis is ready.\nWhat do you want to do?",
                                "ultron": "I was meant\nto be beautiful.",
                                "herbie": "Herbie is active\nWhatcha need?",
                            }[personality])
                            active_personality = personality
                            waiting_for_followup = True
                        else:
                            reply("Say a valid personality name to start.")
                    else:
                        if active_personality:
                            cmds = personalities[active_personality]["commands"]
                            matched = False
                            for keys, action in cmds.items():
                                if command in keys:
                                    result = action()
                                    if result == "quit":
                                        clear()
                                        return
                                    matched = True
                                    break
                            if not matched:
                                reply(f"{active_personality.capitalize()} doesn't understand: {command}")
                        else:
                            reply("No personality is active.")

                        waiting_for_followup = False

                except sr.UnknownValueError:
                    reply("Sorry, I didn't catch that.")
                except sr.RequestError:
                    reply("Speech service unavailable.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    # Command-line argument handling
    if len(sys.argv) == 1:
        print("One of the required arguments is missing. Use 'jarvis start' or 'jarvis help'.")
        sys.exit(1)

    if sys.argv[1].lower() == "help":
        print("""
Jarvis Help Menu
----------------
  jarvis start   - Start the voice assistant
  jarvis help    - Show this help menu

How to Use:
  Hold the 'T' key to talk.
  Say one of the following names to activate a personality:
    - "Jarvis"
    - "Ultron"
    - "Herbie"

Personality Command List:
-------------------------

JARVIS Commands:
  "who am I"                        - Jarvis responds with "Iron Man"
  "clip that"                      - Connects to OBS, records 10 seconds, and saves a clip

ULTRON Commands:
  "scan my network"                - Runs netstat in terminal
  
HERBIE Commands:
  "play my jam"                    - Plays your jam
  "get fantastic"                  - Ain't that fantastic? 

General Commands:
  "quit"                           - Exit the assistant

Notes:
  - Audio recognition uses your microphone.
  - Some commands trigger key presses (NumPad 4–9), ensure related actions/scripts are set up.
  - OBS integration assumes you have OBS running with WebSocket plugin enabled and configured.
        """)
        sys.exit(0)

    elif sys.argv[1].lower() != "start":
        print(f"Unknown command: {sys.argv[1]}")
        print("Use 'jarvis help' for usage information.")
        sys.exit(1)

    # Start the GUI and voice assistant thread
    root = tk.Tk()
    gui = JarvisGUI(root, gui_queue)
    threading.Thread(target=voice_loop, daemon=True).start()
