import speech_recognition as sr
import webbrowser
import time
import os
import obswebsocket
import keyboard
import tkinter as tk
import threading
import queue
import sys

# OBS WebSocket connection info
OBS_HOST = "127.0.0.1"
OBS_PORT = 4444
OBS_PASSWORD = "pass"

gui_queue = queue.Queue()

def reply(text):
    """Push text updates to GUI queue."""
    gui_queue.put(text)

class JarvisGUI:
    """Simple always-on-top GUI for status display."""
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Jarvis")
        self.root.attributes("-topmost", True)
        self.root.geometry("300x100+1600+50")
        self.root.configure(bg="black")
        self.root.overrideredirect(True)  # no window frame
        self.label = tk.Label(self.root, fg="lime", bg="black", font=("Consolas", 12))
        self.label.pack(padx=10, pady=10)
        self.update_gui()

    def update_gui(self):
        """Update label text from queue, then schedule next update."""
        try:
            while True:
                self.label.config(text=self.queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(100, self.update_gui)

def clear_console():
    """Clear console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def record_clip():
    """Record 10-second clip in OBS using WebSocket."""
    client = obswebsocket.obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    try:
        client.connect()
        reply("Connected to OBS.")
        client.call(obswebsocket.requests.StartRecording())
        reply("Recording started...")
        time.sleep(10)
        client.call(obswebsocket.requests.StopRecording())
        reply("Recording stopped.")
    except Exception as e:
        reply(f"OBS Error: {e}")
    finally:
        try:
            if getattr(client, "thread_recv", None):
                client.disconnect()
                reply("Disconnected from OBS.")
        except Exception as e:
            reply(f"Disconnect Error: {e}")

def listen_command(recognizer, prompt="Listening..."):
    """Listen for voice input and return recognized text lowercase."""
    reply(prompt)
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        return recognizer.recognize_google(audio).lower()

def voice_loop():
    recognizer = sr.Recognizer()
    clear_console()
    reply("Jarvis started. Hold 'T' to talk.")
    waiting_for_followup = False
    active_personality = None

    while True:
        try:
            if keyboard.is_pressed("t"):
                try:
                    command = listen_command(recognizer)

                    if not waiting_for_followup:
                        # Activate personality
                        if command in ["hey jarvis", "jarvis"]:
                            clear_console()
                            reply("Jarvis ready. Your command?")
                            active_personality = "jarvis"
                            waiting_for_followup = True
                        elif command in ["ultron", "hey ultron"]:
                            clear_console()
                            reply("Ultron activated.")
                            active_personality = "ultron"
                            waiting_for_followup = True
                        elif command in ["herbie", "hey herbie", "ain't that fantastic"]:
                            clear_console()
                            reply("Herbie online.")
                            active_personality = "herbie"
                            waiting_for_followup = True

                    else:
                        # Process commands by personality
                        if active_personality == "ultron":
                            if command == "scan my network":
                                clear_console()
                                reply("Running network scan...")
                                os.system("netstat")
                            elif command == "quit":
                                clear_console()
                                break
                            else:
                                reply(f"Ultron doesn't understand: {command}")

                        elif active_personality == "herbie":
                            if command == "play my jam":
                                clear_console()
                                reply("Playing jam...")
                                webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                            elif command == "get fantastic":
                                clear_console()
                                reply("Fetching fantastic...")
                                webbrowser.open("https://www.youtube.com/watch?v=_0yhnFeoFhA")
                            elif command == "quit":
                                clear_console()
                                break
                            else:
                                reply(f"Herbie doesn't recognize: {command}")

                        elif active_personality == "jarvis":
                            if command == "clip that":
                                clear_console()
                                record_clip()
                            elif command == "quit":
                                clear_console()
                                break
                            else:
                                reply(f"Jarvis doesn't understand: {command}")

                        else:
                            reply("No active personality.")

                        waiting_for_followup = False

                except sr.UnknownValueError:
                    reply("Sorry, didn't catch that.")
                except sr.RequestError:
                    reply("Speech recognition unavailable.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    # Check CLI args
    if len(sys.argv) < 2:
        print("Missing argument. Use 'jarvis start' or 'jarvis help'.")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "help":
        print("""
Jarvis Help
-----------
Use 'jarvis start' to run the assistant.

Personalities (say name then command):
- Jarvis
- Ultron
- Herbie

Jarvis commands:
- clip that (records 10s OBS clip)
- quit

Ultron commands:
- scan my network
- quit

Herbie commands:
- play my jam 
- get fantastic 
- quit

Hold 'T' to talk.
        """)
        sys.exit(0)

    if cmd != "start":
        print(f"Unknown command: {cmd}")
        print("Use 'jarvis help' for usage info.")
        sys.exit(1)

    root = tk.Tk()
    gui = JarvisGUI(root, gui_queue)
    threading.Thread(target=voice_loop, daemon=True).start()
    root.mainloop()
