# Import required libraries
import speech_recognition as sr  # For voice recognition
import webbrowser  # To open web pages
import time  # For sleep/delay
import pyautogui  # For GUI automation (currently not used directly)
import os  # For system commands
import obswebsocket  # OBS WebSocket client
import keyboard  # To detect keyboard input
import tkinter as tk  # For GUI display
import threading  # To run GUI and logic concurrently
import queue  # To communicate between threads
import sys  # For command-line arguments

# OBS connection settings
OBS_HOST = "127.0.0.1"
OBS_PORT = 4444
OBS_PASSWORD = "pass"

# -----------------------------
# GUI Class for Live Status
# -----------------------------
class JarvisGUI:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Jarvis")
        self.root.attributes("-topmost", True)  # Always on top
        self.root.geometry("300x100+1600+50")  # Position window top-right
        self.root.configure(bg="black")
        self.root.overrideredirect(True)  # Remove window decorations

        # Label for displaying status
        self.label = tk.Label(
            self.root,
            text="Starting...",
            fg="lime",
            bg="black",
            font=("Consolas", 12)
        )
        self.label.pack(padx=10, pady=10)
        self.update_gui()

    # Poll the queue for new messages and update GUI
    def update_gui(self):
        try:
            while True:
                text = self.queue.get_nowait()
                self.label.config(text=text)
                print(text)
        except queue.Empty:
            pass
        self.root.after(100, self.update_gui)

# Clear terminal screen
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# Record a short video clip using OBS
def clip():
    client = obswebsocket.obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    try:
        client.connect()
        gui_queue.put("Connected to OBS Successfully..")

        # Start recording
        client.call(obswebsocket.requests.StartRecording())
        gui_queue.put("Recording Started...")

        time.sleep(10)  # Record for 10 seconds

        # Stop recording
        client.call(obswebsocket.requests.StopRecording())
        gui_queue.put("Recording Stopped...")

    except Exception as e:
        gui_queue.put(f"Error: {e}")

    finally:
        # Disconnect from OBS
        try:
            if getattr(client, "thread_recv", None):
                client.disconnect()
                gui_queue.put("Disconnected from OBS")
            else:
                gui_queue.put("OBS connection not fully established; skipping disconnect.")
        except Exception as e:
            gui_queue.put(f"Error during disconnect: {e}")

# Listen for a voice command
def listen(recognizer, prompt="Listening..."):
    gui_queue.put(prompt)
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        return recognizer.recognize_google(audio).lower()

# Main loop for voice input and command processing
def voice_loop():
    recognizer = sr.Recognizer()
    clear()
    gui_queue.put("Jarvis is starting...\nHold 'T' to talk.")
    waiting_for_followup = False
    active_personality = None  # Current personality context (Jarvis, Ultron, Herbie)

    while True:
        try:
            # Only listen when 'T' is pressed
            if keyboard.is_pressed("t"):
                try:
                    command = listen(recognizer)

                    # No personality active — wait for wake word
                    if not waiting_for_followup:
                        if command in ["hey jarvis", "jarvis"]:
                            clear()
                            gui_queue.put("Hello, Jarvis is ready.\nWhat do you want to do?")
                            active_personality = "jarvis"
                            waiting_for_followup = True
                        elif command in ["ultron", "hey ultron"]:
                            clear()
                            gui_queue.put("I was meant\nto be beautiful.")
                            active_personality = "ultron"
                            waiting_for_followup = True
                        elif command in ["herbie", "hey herbie", "ain't that fantastic"]:
                            clear()
                            gui_queue.put("Herbie is active\nWhatcha need?")
                            active_personality = "herbie"
                            waiting_for_followup = True

                    # Process command under current personality
                    else:
                        if active_personality == "ultron":
                            if command == "scan my network":
                                clear()
                                gui_queue.put("Scanning your network...")
                                os.system("netstat")  # Show active connections
                            elif command == "quit":
                                clear()
                                break
                            else:
                                gui_queue.put(f"Ultron doesn't understand: {command}")

                        elif active_personality == "herbie":
                            if command == "play my jam":
                                clear()
                                gui_queue.put("Playing your jam...")
                                webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Rickroll
                            elif command == "get fantastic":
                                clear()
                                gui_queue.put("Getting Fantastic...")
                                webbrowser.open("https://www.youtube.com/watch?v=_0yhnFeoFhA")
                            elif command == "quit":
                                clear()
                                break
                            else:
                                gui_queue.put(f"Herbie doesn't recognize: {command}")

                        elif active_personality == "jarvis":
                            if command == "clip that":
                                clear()
                                clip()
                            elif command == "quit":
                                clear()
                                break
                            else:
                                gui_queue.put(f"Jarvis doesn't understand: {command}")

                        else:
                            gui_queue.put("No personality is active.")

                        # Reset to listen for a new personality activation
                        waiting_for_followup = False

                except sr.UnknownValueError:
                    gui_queue.put("Sorry, I didn't catch that.")
                except sr.RequestError:
                    gui_queue.put("Speech service unavailable.")
        except KeyboardInterrupt:
            break

# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__": 
    # Check if arguments are provided
    if len(sys.argv) == 1:
        print("One of the required arguments is missing. Use 'jarvis start' or 'jarvis help'.")
        sys.exit(1)

    # Help Menu
    if sys.argv[1].lower() == "help":
        print("""
Jarvis Help Menu
----------------
  jarvis start   - Start the voice assistant
  jarvis help    - Show this help menu

How to Use:
  Hold the 'T' key to talk.
  Say one of the following names to activate a personality (Must specify personality each time):
    - "Jarvis"
    - "Ultron"
    - "Herbie"

Personality Command List:
-------------------------

JARVIS Commands:
  "clip that"                      - Connects to OBS, records 10 seconds, and saves a clip

ULTRON Commands:
  "scan my network"                - Runs netstat in terminal
  
HERBIE Commands:
  "play my jam"                    - Opens Rick Astley's "Never Gonna Give You Up"
  "get fantastic"                  - Opens a Fantastic Four meme clip

General Commands:
  "quit"                           - Exit the assistant

Notes:
  - Audio recognition uses your microphone.
  - OBS integration assumes OBS is running with WebSocket plugin enabled.
        """)
        sys.exit(0)

    # Start the assistant
    elif sys.argv[1].lower() != "start":
        print(f"Unknown command: {sys}
