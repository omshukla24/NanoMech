# 🤖 NanoMech — AI Visual Chart Analysis Agent
> **Gemini Live Agent Challenge 2026 | Category: UI Navigator**

NanoMech is a real-time AI trading assistant that **sees your trading screen**, sends it to **Google Gemini 2.5 Flash** for multimodal vision analysis, and overlays a complete professional trade setup directly on top of your chart — without ever leaving your trading platform.

---

## 🎯 What NanoMech Does

NanoMech uses Gemini's multimodal vision to read ANY crypto chart on your screen and instantly delivers two overlay panels:

**Overlay 1 — Market Analysis & Liquidity:**
- **• Trend** — Market structure, moving average crossovers, bullish/bearish bias (3-4 sentence depth)
- **• Liquidity** — Order book depth, bid/ask walls, key support/resistance zones
- **• Momentum** — Candlestick patterns, volume behavior, price velocity

**Overlay 2 — Trade Setup + Risk Calculator:**
- **Entry** — AI-identified optimal entry price
- **Target** — Take-profit price level
- **Stop** — Stop-loss price level
- **CALC:**
  - **Risk Amt** — Dollar risk based on your entered Risk %
  - **Size** — Position size in units
  - **R:R Ratio** — Risk-to-reward ratio

---

## ✨ Features

| Feature | Detail |
|---|---|
| 👁️ Visual chart reading | Captures screen with `mss`, sends image to Gemini 2.5 Flash |
| 🧮 Live risk calculator | Type Risk % → Risk Amt, Size, R:R update instantly |
| 🔄 Auto mode | Re-scans every 20 seconds |
| ⌨️ Hotkey | `Ctrl+A+I` to scan without touching the mouse |
| 🪟 Floating overlays | Draggable, resizable, transparent panels over any app |
| 📋 Session logs | Saves chart screenshot + trade_data.txt per scan, auto-cleaned after 7 days |

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| Google Gemini 2.5 Flash | Multimodal vision model — reads and interprets chart screenshots |
| Google GenAI SDK (`google-genai`) | Official Python SDK, calls Gemini on Google Cloud |
| Google Cloud AI Infrastructure | Powers all Gemini model inference |
| Python 3.10+ | Core application language |
| Tkinter | Frameless always-on-top overlay GUI |
| mss | Fast cross-platform screen capture |
| Pillow / PIL | Image processing before API call |
| keyboard | Global hotkey listener |
| python-dotenv | Secure API key management |

---

## ⚙️ Setup & Run

### Prerequisites
- Python 3.10 or higher
- A Gemini API key — [get one free at Google AI Studio](https://aistudio.google.com/app/apikey)

### Step 1 — Clone the repo
```bash
git clone https://github.com/omshukla24/NanoMech.git
cd nanomech
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Configure your API key
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 4 — Run
```bash
python nanomech.py
```
> **Windows users:** Run terminal as Administrator for the global `Ctrl+A+I` hotkey to work.

---

## 🖥️ How to Use

1. Open any crypto chart (TradingView, Binance, Bybit, or any platform)
2. Launch NanoMech — two transparent overlay panels appear on screen
3. Set your **Risk %** in Overlay 2 (default is 5.0)
4. Press **SCAN NOW** or `Ctrl+A+I`
5. NanoMech captures the screen → sends to Gemini → analysis appears in seconds
6. Read your results:
   - Overlay 1: Trend, Liquidity, Momentum
   - Overlay 2: Entry, Target, Stop — then CALC shows Risk Amt, Size, R:R Ratio
7. Change Risk % anytime — numbers update live
8. Toggle **Auto Mode** for hands-free scanning every 20 seconds

---

## 📦 Windows EXE (No Python required)

Pre-built executable available in [Releases](https://github.com/YOUR_USERNAME/nanomech/releases):
1. Download `NanoMech.exe`
2. Place a `.env` file with your API key in the same folder
3. Double-click to launch

---

## 📁 Project Structure

```
nanomech/
├── nanomech.py           # Main application
├── requirements.txt      # Python dependencies
├── .env.example          # API key template (copy to .env)
├── .gitignore
├── README.md
└── Logs/                 # Auto-created per session
    └── Session_YYYY-MM-DD_HH-MM-SS/
        └── Scan_1_HH-MM-SS/
            ├── trade_data.txt          # AI analysis output
            ├── 1_analyzed_chart.png    # Chart that was scanned
            └── 2_overlay_result.png    # Full screen with overlays
```

---

## ☁️ Google Cloud Integration

Every scan calls **Gemini 2.5 Flash** via the Google GenAI SDK. All inference runs on **Google Cloud AI infrastructure**:

```python
from google import genai

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model='gemini-2.5-flash',   # Hosted on Google Cloud
    contents=[prompt, img]       # Multimodal: text prompt + screenshot image
)
```

Google Cloud powers every single trade analysis NanoMech produces.

---

## 🔒 Security
- `.env` is in `.gitignore` — API key is never committed to the repo
- No data sent anywhere except Google's official Gemini API endpoint

---

## 📄 License
MIT License

*Built for the **Gemini Live Agent Challenge 2026** | #GeminiLiveAgentChallenge*
"# Nano_Mech" 
