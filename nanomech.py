import os
import sys
import mss
import keyboard
import threading
import tkinter as tk
import datetime
import re
import time
import shutil
from PIL import Image
from google import genai
from dotenv import load_dotenv

# ==========================================
# CONFIGURATION
# ==========================================
ACCOUNT_BALANCE = 1000.0 

if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(app_path, '.env')
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    sys.exit()

try:
    client = genai.Client(api_key=api_key)
except Exception:
    sys.exit()

class CryptoOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() 

        # Theme Colors
        self.bg_color = "#121212"       
        self.title_color = "#00FFC2"    # Cyan Green (Used for Titles and CALC)
        self.accent_color = "#FF3366"   # Red (Used for Entry, Target, Size, etc.)
        self.active_green = "#00FF7F"   # Neon Green (Active Buttons)
        self.text_color = "#E0E0E0"     
        self.drag_color = "#1F1F1F"     
        
        self.font_main = ("Segoe UI", 11)
        self.font_bold = ("Segoe UI", 11, "bold")

        self.is_analyzing = False
        self.auto_refresh = False
        self.refresh_interval = 20000 
        self.spin_angle = 0
        self.scan_count = 0
        
        self.current_entry = 0.0
        self.current_stop = 0.0
        self.current_target = 0.0
        self.current_t_formatted = "" 

        self.cleanup_old_logs()

        self.session_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = os.path.join(app_path, "Logs", f"Session_{self.session_time}")
        os.makedirs(self.session_dir, exist_ok=True)

        # --- OVERLAY 1: Market Analysis ---
        self.win1 = self.create_overlay("420x550+20+20", self.bg_color, 0.85, show_auto=True) # Made default height taller for more text
        tk.Label(self.win1.content_frame, text="MARKET ANALYSIS & LIQUIDITY", font=self.font_bold, bg=self.bg_color, fg=self.title_color).pack(side="top", pady=(15, 10))
        
        self.btn_scan = tk.Button(self.win1.content_frame, text="SCAN NOW", font=("Segoe UI", 9, "bold"), bg=self.drag_color, fg="white", activebackground=self.active_green, bd=0, padx=25, pady=8, cursor="hand2", command=self.toggle_auto)
        self.btn_scan.pack(side="bottom", pady=(0, 15))

        self.canvas1 = tk.Canvas(self.win1.content_frame, width=50, height=50, bg=self.bg_color, highlightthickness=0)
        self.txt_data1 = tk.Text(self.win1.content_frame, font=self.font_main, bg=self.bg_color, fg=self.text_color, wrap="word", bd=0, highlightthickness=0)
        self.txt_data1.pack(side="top", padx=15, pady=5, fill="both", expand=True)
        self.txt_data1.tag_configure("topic", font=self.font_bold, foreground=self.accent_color)
        self.txt_data1.insert("1.0", "Standing by...")
        self.txt_data1.config(state=tk.DISABLED)

        self.win1.grip.lift()

        # --- OVERLAY 2: Trade Setup ---
        self.win2 = self.create_overlay("420x350+20+590", self.bg_color, 0.90, show_auto=False)
        tk.Label(self.win2.content_frame, text="TRADE SETUP", font=self.font_bold, bg=self.bg_color, fg=self.title_color).pack(side="top", pady=(15, 10))

        risk_frame = tk.Frame(self.win2.content_frame, bg=self.bg_color)
        risk_frame.pack(side="top", fill="x", padx=15)
        tk.Label(risk_frame, text="Risk %:", font=self.font_bold, bg=self.bg_color, fg=self.accent_color).pack(side="left")
        self.risk_input = tk.Entry(risk_frame, width=6, font=self.font_bold, bg=self.drag_color, fg="white", bd=0, insertbackground="white")
        self.risk_input.pack(side="left", padx=5)
        self.risk_input.insert(0, "5.0")
        self.risk_input.bind("<KeyRelease>", lambda e: self.update_math_ui())

        self.canvas2 = tk.Canvas(self.win2.content_frame, width=50, height=50, bg=self.bg_color, highlightthickness=0)
        self.txt_data2 = tk.Text(self.win2.content_frame, font=("Segoe UI", 12), bg=self.bg_color, fg=self.text_color, wrap="word", bd=0, highlightthickness=0)
        self.txt_data2.pack(side="top", padx=15, pady=10, fill="both", expand=True)
        
        self.txt_data2.tag_configure("topic", font=("Segoe UI", 12, "bold"), foreground=self.accent_color)
        self.txt_data2.tag_configure("calc_title", font=("Segoe UI", 12, "bold"), foreground=self.title_color, justify="center") # Cyan Green
        
        self.txt_data2.insert("1.0", "Awaiting scan...")
        self.txt_data2.config(state=tk.DISABLED)

        self.win2.grip.lift()

        keyboard.add_hotkey('ctrl+a+i', self.start_analysis_thread)
        keyboard.add_hotkey('esc', self.quit_app)

    def cleanup_old_logs(self):
        try:
            log_dir = os.path.join(app_path, "Logs")
            if not os.path.exists(log_dir): return
            now = time.time()
            for folder in os.listdir(log_dir):
                folder_path = os.path.join(log_dir, folder)
                if os.path.isdir(folder_path):
                    if os.stat(folder_path).st_mtime < now - 604800:
                        shutil.rmtree(folder_path)
        except: pass

    def create_overlay(self, geometry, bg_color, alpha, show_auto):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True, "-alpha", alpha)
        win.geometry(geometry)
        win.configure(bg=bg_color)
        
        win.title_bar = tk.Frame(win, bg=self.drag_color, height=30)
        win.title_bar.pack(fill="x", side="top")
        win.title_bar.pack_propagate(False) 
        
        drag_handle = tk.Label(win.title_bar, text="≡", bg=self.drag_color, fg="#888888", font=("Segoe UI", 14), cursor="fleur")
        drag_handle.pack(side="left", padx=(10, 5))
        drag_handle.bind("<Button-1>", lambda e: self.start_drag(e, win))
        drag_handle.bind("<B1-Motion>", lambda e: self.do_drag(e, win))

        if show_auto:
            self.btn_auto = tk.Button(win.title_bar, text="Auto: OFF", bg=self.drag_color, fg="#888888", bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", command=self.toggle_auto)
            self.btn_auto.pack(side="left", padx=5)

        tk.Button(win.title_bar, text="✕", bg=self.drag_color, fg="#FF3366", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", command=self.quit_app).pack(side="right", padx=10)

        win.content_frame = tk.Frame(win, bg=bg_color)
        win.content_frame.pack(fill="both", expand=True)

        win.grip = tk.Label(win.content_frame, text="◢", bg=bg_color, fg="#555555", font=("Segoe UI", 12), cursor="size_nw_se")
        win.grip.place(relx=1.0, rely=1.0, anchor="se")
        win.grip.bind("<B1-Motion>", lambda e: self.resize_window(e, win))

        return win

    def resize_window(self, event, win):
        new_width = max(300, event.x_root - win.winfo_rootx())
        new_height = max(200, event.y_root - win.winfo_rooty())
        win.geometry(f"{new_width}x{new_height}")

    def toggle_auto(self):
        self.auto_refresh = not self.auto_refresh
        if self.auto_refresh:
            if hasattr(self, 'btn_auto'): self.btn_auto.config(text="Auto: ON", fg=self.active_green)
            self.btn_scan.config(text="STOP", bg=self.active_green, fg="black")
            self.start_analysis_thread()
        else:
            if hasattr(self, 'btn_auto'): self.btn_auto.config(text="Auto: OFF", fg="#888888")
            self.btn_scan.config(text="SCAN NOW", bg=self.drag_color, fg="white")

    def start_drag(self, event, win): win._x = event.x; win._y = event.y
    def do_drag(self, event, win): win.geometry(f"+{event.x_root - win._x}+{event.y_root - win._y}")

    def update_math_ui(self):
        if self.is_analyzing: return
        if self.current_entry <= 0 or self.current_stop <= 0: return
        try:
            risk_pct = float(self.risk_input.get()) / 100
            if risk_pct <= 0: return
            risk_amt = ACCOUNT_BALANCE * risk_pct
            dist = abs(self.current_entry - self.current_stop)
            reward = abs(self.current_target - self.current_entry)
            size = risk_amt / dist if dist != 0 else 0
            rr = reward / dist if dist != 0 else 0

            self.txt_data2.config(state=tk.NORMAL)
            self.txt_data2.delete("1.0", tk.END)
            
            if self.current_t_formatted:
                self.insert_tags(self.txt_data2, self.current_t_formatted)

            self.txt_data2.insert(tk.END, "\n\nCALC\n\n", "calc_title")

            math_display = (
                f"**Risk Amt:** ${risk_amt:.2f}\n\n"
                f"**Size:** {size:.4f} Units\n\n"
                f"**R:R Ratio:** {rr:.2f}"
            )
            self.insert_tags(self.txt_data2, math_display)
            self.txt_data2.config(state=tk.DISABLED)
        except:
            pass

    def insert_tags(self, widget, text, tag_override=None):
        parts = text.split("**")
        is_bold = False
        for part in parts:
            tag = (tag_override if tag_override else "topic") if is_bold else "normal"
            widget.insert(tk.END, part, tag)
            is_bold = not is_bold

    def type_writer(self, widget, text, index=0, is_bold=False):
        if self.is_analyzing: return
        widget.config(state=tk.NORMAL)
        if index == 0: widget.delete("1.0", tk.END)
        if index < len(text):
            if text[index:index+2] == "**":
                is_bold = not is_bold
                self.root.after(0, self.type_writer, widget, text, index+2, is_bold)
                return
            tag = "topic" if is_bold else "normal"
            widget.insert(tk.END, text[index], tag)
            widget.config(state=tk.DISABLED)
            self.root.after(10, self.type_writer, widget, text, index+1, is_bold)
        else:
            if widget == self.txt_data2: self.update_math_ui()

    def animate(self):
        if not self.is_analyzing:
            self.canvas1.pack_forget(); self.canvas2.pack_forget()
            self.txt_data1.pack(side="top", fill="both", expand=True, padx=15)
            self.txt_data2.pack(side="top", fill="both", expand=True, padx=15)
            return
        self.canvas1.delete("all"); self.canvas2.delete("all")
        self.spin_angle = (self.spin_angle + 20) % 360
        for c in [self.canvas1, self.canvas2]:
            c.create_arc(5, 5, 45, 45, start=self.spin_angle, extent=100, outline=self.accent_color, width=4, style=tk.ARC)
        self.root.after(40, self.animate)

    def log_analysis(self, analysis_text, trade_text, img):
        self.scan_count += 1
        scan_time = datetime.datetime.now().strftime("%H-%M-%S")
        folder = os.path.join(self.session_dir, f"Scan_{self.scan_count}_{scan_time}")
        os.makedirs(folder, exist_ok=True)
        
        clean_a = analysis_text.replace("**", "")
        clean_t = trade_text.replace("**", "")
        
        with open(os.path.join(folder, "trade_data.txt"), "w", encoding="utf-8") as f:
            f.write(f"=== MARKET ANALYSIS ===\n{clean_a}\n\n=== TRADE SETUP ===\n{clean_t}")
            
        img.save(os.path.join(folder, "1_analyzed_chart.png"))
        return folder

    def save_overlay_screenshot(self, folder):
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.bgra, "raw", "BGRX")
                img.save(os.path.join(folder, "2_overlay_result.png"))
        except: pass

    def start_analysis_thread(self):
        if self.is_analyzing: return
        self.is_analyzing = True
        self.txt_data1.pack_forget(); self.txt_data2.pack_forget()
        self.canvas1.pack(side="top", pady=30); self.canvas2.pack(side="top", pady=20)
        self.animate()
        threading.Thread(target=self.analyze, daemon=True).start()

    def analyze(self):
        try:
            with mss.mss() as sct:
                time.sleep(0.1)
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.bgra, "raw", "BGRX")
                
                # UPDATED PROMPT: Demanding 3-4 detailed lines for depth
                prompt = """Analyze crypto chart. Return EXACTLY:
                [ANALYSIS]
                **• Trend:** (Provide a detailed 3 to 4 sentence analysis)
                **• Liquidity:** (Provide a detailed 3 to 4 sentence analysis)
                **• Momentum:** (Provide a detailed 3 to 4 sentence analysis)
                [TRADE]
                **Entry:** [Price]
                **Target:** [Price]
                **Stop:** [Price]"""
                
                response = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt, img])
                
                raw_text = response.text
                if "[TRADE]" in raw_text:
                    parts = raw_text.split("[TRADE]")
                    a = parts[0].replace("[ANALYSIS]", "").strip()
                    t = parts[1].strip()
                else:
                    a = raw_text.replace("[ANALYSIS]", "").strip()
                    t = "Format Error from AI."

                a = re.sub(r'(?i)\n*\*\*• Liquidity:\*\*', '\n\n**• Liquidity:**', a)
                a = re.sub(r'(?i)\n*\*\*• Momentum:\*\*', '\n\n**• Momentum:**', a)

                e_match  = re.search(r"Entry[^\d]*([\d.]+)",  t, re.IGNORECASE)
                ta_match = re.search(r"Target[^\d]*([\d.]+)", t, re.IGNORECASE)
                s_match  = re.search(r"Stop[^\d]*([\d.]+)",   t, re.IGNORECASE)

                e_val = e_match.group(1) if e_match else "0.0"
                ta_val = ta_match.group(1) if ta_match else "0.0"
                s_val = s_match.group(1) if s_match else "0.0"

                self.current_entry = float(e_val)
                self.current_target = float(ta_val)
                self.current_stop = float(s_val)

                self.current_t_formatted = f"**Entry:** {e_val}\n\n**Target:** {ta_val}\n\n**Stop:** {s_val}"

                scan_folder = None
                if "Error" not in t:
                    scan_folder = self.log_analysis(a, self.current_t_formatted, img)

                self.root.after(0, self.finish, a, self.current_t_formatted, scan_folder)
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.finish, f"ERROR:\n\n{error_msg[:60]}", "Check connection", None)

    def finish(self, a, t, scan_folder=None):
        self.is_analyzing = False
        self.type_writer(self.txt_data1, a)
        self.type_writer(self.txt_data2, t)

        delay = len(t) * 10 + 200
        self.root.after(delay, self.update_math_ui)

        if scan_folder:
            self.root.after(9000, lambda: self.save_overlay_screenshot(scan_folder))
            
        if self.auto_refresh: 
            self.root.after(self.refresh_interval, self.start_analysis_thread)

    def quit_app(self): self.root.destroy(); sys.exit()
    def run(self): self.root.mainloop()

if __name__ == "__main__":
    app = CryptoOverlay()
    app.run()