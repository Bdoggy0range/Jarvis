# 🎙️ Jarvis

A simple voice-activated assistant with multiple personalities (**Jarvis**, **Ultron**, **Herbie**) built using Python, integrating features like OBS recording, browser automation, system commands, and a real-time floating GUI.

## 🧠 Features

* **Voice Activation** (via microphone)
* **Multiple Personalities**:

  * **Jarvis** – Performs screen recording via OBS
  * **Ultron** – Executes network scans
  * **Herbie** – Plays internet memes/music
* **OBS WebSocket Integration** (for automated screen recordings)
* **Live GUI Feedback** using Tkinter
* **Keyboard Control**: Hold `T` to talk

---

## 🚀 Getting Started

### 🔧 Requirements

Ensure the following Python packages are installed:

```bash
pip install SpeechRecognition pyautogui keyboard obs-websocket-py
```

Also required:

* Python 3.7+
* [OBS Studio](https://obsproject.com/).

### 🖥️ OBS Configuration

* Enable the WebSocket server in OBS settings.
* Default host: `127.0.0.1`
* Default port: `4444`
* Set password in code (`OBS_PASSWORD`) to match OBS settings.

---

## ▶️ Usage

Run the assistant using:

```bash
python jarvis.py start
```

Or show help info:

```bash
python jarvis.py help
```

---

## 🗣️ Voice Commands

> Hold down the `T` key and speak clearly into your microphone.

### 🧔 Jarvis Commands

| Command     | Description                             |
| ----------- | --------------------------------------- |
| `clip that` | Records a 10-second screen clip via OBS |

### 🤖 Ultron Commands

| Command           | Description                |
| ----------------- | -------------------------- |
| `scan my network` | Runs `netstat` in terminal |

### 🚗 Herbie Commands

| Command         | Description                                   |
| --------------- | --------------------------------------------- |
| `play my jam`   | Plays Rick Astley's "Never Gonna Give You Up" |
| `get fantastic` | Opens a Fantastic Four meme video             |

### ❌ Universal Command

| Command | Description         |
| ------- | ------------------- |
| `quit`  | Exits the assistant |

---

## 🧩 Personalities

Before issuing any commands, activate a personality:

| Activation Phrase | Personality |
| ----------------- | ----------- |
| `Hey Jarvis`      | Jarvis      |
| `Hey Ultron`      | Ultron      |
| `Hey Herbie`      | Herbie      |

You must activate a personality each time before giving a command.

---

## 🪟 GUI

A compact floating GUI shows current status and feedback in real time:

* Always on top
* Located in the top-right of the screen
* Updates based on what Jarvis hears and does

---

## 🛠️ Troubleshooting

* If microphone doesn't work, check your device input settings.
* If OBS recording fails, verify OBS is running and the WebSocket server is enabled with correct port/password.
* Voice recognition may be inaccurate in noisy environments.

---

## 📁 Project Structure (Key Components)

| File/Function  | Purpose                                      |
| -------------- | -------------------------------------------- |
| `clip()`       | Handles OBS screen recording                 |
| `listen()`     | Captures audio input using SpeechRecognition |
| `voice_loop()` | Main command loop for listening and handling |
| `JarvisGUI`    | Tkinter class for displaying status updates  |
| `obswebsocket` | Python OBS WebSocket client                  |

---

## 📌 Notes

* `pyautogui`, `keyboard`, and OBS WebSocket can affect your system or apps. Use responsibly.
* This is a prototype/demo; it's not secure or production-ready.
* Extend it with your own personalities or integrate APIs for more functionality!
* OBS is currently broken will fix

---

## 🧑‍💻 Author

Created by BdoggyOrange – Inspired by Marvel's AI characters

---

## 📜 License

This project is open-source. Feel free to modify and extend.

---

Let me know if you want this in Markdown file format (`README.md`) or want to add installation scripts!
