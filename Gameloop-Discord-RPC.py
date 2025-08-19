import psutil
import subprocess
import os
import re
import time
import threading
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Optional, Dict
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pystray
from PIL import Image, ImageTk
from pypresence import Presence
import webbrowser
import requests
from io import BytesIO


class GameloopRPC:
    def __init__(self):
        self.discord_client_id = "1407470684803829942"
        self.discord_rpc = None
        self.current_app = None
        self.current_status = None  
        self.running = False
        self.monitor_thread = None  
        self.gameloop_start_time = None
        self.last_focus_time = None
        self.idle_threshold = 300  
        
        
        self.games = {
            'com.android.launcherex': {'name': 'Launcher UI', 'icon': 'launcher_ui'},
            'com.android.settings': {'name': 'Settings', 'icon': 'settings'},
            'nextapp.fx': {'name': 'FX File Explorer', 'icon': 'fx'},
            'com.android.vending': {'name': 'Google Play Store', 'icon': 'google_play_store'},
            'com.google.android.play.games': {'name': 'Google Play Games', 'icon': 'google_play_games'},
            'com.whatsapp': {'name': 'WhatsApp', 'icon': 'whatsapp'},
            'com.facebook.katana': {'name': 'Facebook', 'icon': 'facebook'},
            'com.twitter.android': {'name': 'Twitter', 'icon': 'twitter'},
            'com.google.android.youtube': {'name': 'YouTube', 'icon': 'youtube'},
            'com.tencent.ig': {'name': 'PUBG Mobile', 'icon': 'pubg_mobile'},
            'com.activision.callofduty.shooter': {'name': 'Call of Duty Mobile', 'icon': 'cod_mobile'},
            'com.garena.game.freefire': {'name': 'Free Fire', 'icon': 'free_fire'},
        }
        
        self.gameloop_process = "AndroidEmulatorEn.exe"
        self.adb_path = None
        self.update_interval = 10
        self.user32 = ctypes.windll.user32
        self.tray_icon = None
        
        
        self.contact_icons = {}
        self.icon_urls = {
            'discord': 'https://cdn-icons-png.flaticon.com/512/5968/5968756.png',
            'github': 'https://cdn-icons-png.flaticon.com/512/1051/1051326.png',
            'instagram': 'https://cdn-icons-png.flaticon.com/512/3955/3955024.png'
        }
        
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Gameloop Discord Rich Presence")
        self.root.geometry("500x450")  
        self.root.resizable(True, True)
        
        
        self.root.grid_rowconfigure(2, weight=1)  
        self.root.grid_columnconfigure(0, weight=1)
        
        
        status_frame = ttk.LabelFrame(self.root, text="Status", padding="10")
        status_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        status_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Discord:").grid(row=0, column=0, sticky="w")
        self.discord_status = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.discord_status.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(status_frame, text="Gameloop:").grid(row=1, column=0, sticky="w")
        self.gameloop_status = ttk.Label(status_frame, text="Not Running", foreground="red")
        self.gameloop_status.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(status_frame, text="Current Game:").grid(row=2, column=0, sticky="w")
        self.game_status = ttk.Label(status_frame, text="None")
        self.game_status.grid(row=2, column=1, sticky="w", padx=(10, 0))
        
        
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start RPC", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop RPC", command=self.stop_monitoring, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(control_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Minimize to Tray", command=self.minimize_to_tray).grid(row=0, column=3, padx=5)
        
        
        log_frame = ttk.LabelFrame(self.root, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=60)  
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        
        contact_frame = ttk.LabelFrame(self.root, text="Contact", padding="10")
        contact_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        contact_frame.grid_columnconfigure(0, weight=1)
        
        
        contact_info_frame = ttk.Frame(contact_frame)
        contact_info_frame.grid(row=0, column=0)
        
        
        discord_frame = ttk.Frame(contact_info_frame)
        discord_frame.grid(row=0, column=0, padx=10, pady=2)
        
        self.discord_icon = ttk.Label(discord_frame, text="DC", foreground="#7289DA", font=("Arial", 10, "bold"))
        self.discord_icon.grid(row=0, column=0, padx=(0, 5))
        
        discord_link = ttk.Label(discord_frame, text="@sp1_", foreground="blue", cursor="hand2", font=("Arial", 10))
        discord_link.grid(row=0, column=1)
        discord_link.bind("<Button-1>", lambda e: self.copy_to_clipboard("sp1_"))
        discord_link.bind("<Enter>", lambda e: discord_link.config(foreground="darkblue"))
        discord_link.bind("<Leave>", lambda e: discord_link.config(foreground="blue"))
        
        
        github_frame = ttk.Frame(contact_info_frame)
        github_frame.grid(row=0, column=1, padx=10, pady=2)
        
        self.github_icon = ttk.Label(github_frame, text="GH", foreground="#333", font=("Arial", 10, "bold"))
        self.github_icon.grid(row=0, column=0, padx=(0, 5))
        
        github_link = ttk.Label(github_frame, text="@iMikano", foreground="blue", cursor="hand2", font=("Arial", 10))
        github_link.grid(row=0, column=1)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/iMikano"))
        github_link.bind("<Enter>", lambda e: github_link.config(foreground="darkblue"))
        github_link.bind("<Leave>", lambda e: github_link.config(foreground="blue"))
        
        
        instagram_frame = ttk.Frame(contact_info_frame)
        instagram_frame.grid(row=0, column=2, padx=10, pady=2)
        
        self.instagram_icon = ttk.Label(instagram_frame, text="IG", foreground="#E4405F", font=("Arial", 10, "bold"))
        self.instagram_icon.grid(row=0, column=0, padx=(0, 5))
        
        instagram_link = ttk.Label(instagram_frame, text="@var.mikano", foreground="blue", cursor="hand2", font=("Arial", 10))
        instagram_link.grid(row=0, column=1)
        instagram_link.bind("<Button-1>", lambda e: webbrowser.open("https://instagram.com/var.mikano"))
        instagram_link.bind("<Enter>", lambda e: instagram_link.config(foreground="darkblue"))
        instagram_link.bind("<Leave>", lambda e: instagram_link.config(foreground="blue"))
        
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
        self.setup_tray()
        
        
        self.load_contact_icons()
        
        
        self.update_contact_icons()
    
    def load_contact_icons(self):
        for platform, url in self.icon_urls.items():
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                
                image = Image.open(BytesIO(response.content))
                image = image.resize((24, 24), Image.Resampling.LANCZOS)
                
                
                self.contact_icons[platform] = ImageTk.PhotoImage(image)
                
            except Exception as e:
                print(f"Failed to load {platform} icon: {e}")
                
    
    def update_contact_icons(self):
        if 'discord' in self.contact_icons and hasattr(self, 'discord_icon'):
            self.discord_icon.config(image=self.contact_icons['discord'], text="")
        
        if 'github' in self.contact_icons and hasattr(self, 'github_icon'):
            self.github_icon.config(image=self.contact_icons['github'], text="")
        
        if 'instagram' in self.contact_icons and hasattr(self, 'instagram_icon'):
            self.instagram_icon.config(image=self.contact_icons['instagram'], text="")
    
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  
        self.log(f"Copied '{text}' to clipboard")
        
    def setup_tray(self):
        try:
            
            image = Image.new('RGB', (64, 64), color='#7289DA')
            
            menu = pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Hide", self.minimize_to_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start RPC", self.start_monitoring),
                pystray.MenuItem("Stop RPC", self.stop_monitoring),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.quit_application)
            )
            
            self.tray_icon = pystray.Icon(
                "gameloop_rpc",
                image,
                "Gameloop Discord RPC",
                menu
            )
        except Exception as e:
            self.log(f"System tray setup failed: {e}")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        
        print(log_message.strip())
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def minimize_to_tray(self):
        if self.tray_icon:
            self.root.withdraw()
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def show_window(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.deiconify()
        self.root.lift()
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? (You can minimize to tray instead)"):
            self.quit_application()
    
    def quit_application(self, icon=None, item=None):
        self.running = False
        
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        
        if self.discord_rpc:
            try:
                self.discord_rpc.clear()
                self.discord_rpc.close()
            except:
                pass
        if self.tray_icon:
            self.tray_icon.stop()
            
        self.root.quit()
        self.root.destroy()
    
    def connect_discord(self):
        try:
            if self.discord_rpc:
                try:
                    self.discord_rpc.close()
                except:
                    pass
            
            self.discord_rpc = Presence(self.discord_client_id)
            self.discord_rpc.connect()
            self.discord_status.config(text="Connected", foreground="green")
            self.log("Connected to Discord")
            return True
        except Exception as e:
            self.discord_status.config(text="Failed", foreground="red")
            self.log(f"Discord connection failed: {e}")
            self.discord_rpc = None
            return False
    
    def is_discord_connected(self):
        if not self.discord_rpc:
            return False
        try:
            
            self.discord_rpc.update()
            return True
        except Exception:
            return False
    
    def is_gameloop_running(self):
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'] == self.gameloop_process:
                    return True
            return False
        except:
            return False
    
    def is_gameloop_focused(self):
        try:
            hwnd = self.user32.GetForegroundWindow()
            if hwnd == 0:
                return False
            
            pid = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            try:
                process = psutil.Process(pid.value)
                return process.name() == self.gameloop_process
            except:
                return False
        except:
            return False
    
    def find_adb_path(self):
        if self.adb_path and os.path.exists(self.adb_path):
            return self.adb_path
        
        
        try:
            for process in psutil.process_iter(['pid', 'name', 'exe']):
                if process.info['name'] == self.gameloop_process and process.info['exe']:
                    gameloop_dir = Path(process.info['exe']).parent
                    search_dirs = [gameloop_dir, gameloop_dir / "ui", gameloop_dir / "AppMarket"]
                    
                    for search_dir in search_dirs:
                        adb_file = search_dir / "adb.exe"
                        if adb_file.exists():
                            self.adb_path = str(adb_file)
                            return self.adb_path
                    break
        except:
            pass
        
        
        try:
            subprocess.run(['adb', 'version'], capture_output=True, check=True, 
                         creationflags=subprocess.CREATE_NO_WINDOW)
            self.adb_path = 'adb'
            return 'adb'
        except:
            pass
        
        return None
    
    def connect_emulator(self):
        adb = self.find_adb_path()
        if not adb:
            return False
        
        try:
            
            result = subprocess.run([adb, 'devices'], capture_output=True, text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                if any('device' in line for line in lines if line.strip()):
                    return True
            
            
            for port in ['5555', '5554', '7555']:
                try:
                    subprocess.run([adb, 'connect', f'127.0.0.1:{port}'], 
                                 capture_output=True, timeout=3,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
                    result = subprocess.run([adb, 'devices'], capture_output=True, text=True,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
                    if 'device' in result.stdout:
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def get_current_app(self):
        adb = self.find_adb_path()
        if not adb or not self.connect_emulator():
            return None
        
        try:
            result = subprocess.run([adb, 'shell', 'dumpsys', 'activity', 'activities'], 
                                  capture_output=True, text=True, timeout=8,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode != 0:
                return None
            
            patterns = [
                r'mResumedActivity.*ActivityRecord{.*?\s+(\S+)/\S+',
                r'mFocusedActivity.*ActivityRecord{.*?\s+(\S+)/\S+',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, result.stdout)
                if matches:
                    return matches[0]
            
            return None
        except:
            return None
    
    def get_game_info(self, package):
        return self.games.get(package, {'name': package, 'icon': 'android'})
    
    def is_idle(self):
        if self.last_focus_time is None:
            return False
        return (time.time() - self.last_focus_time) > self.idle_threshold
    
    def update_presence(self, game_info):
        if not self.discord_rpc:
            return False
        
        try:
            state = "Idle" if self.is_idle() else "Playing"
            
            self.discord_rpc.update(
                details=game_info['name'],
                state=state,
                large_image='gameloop-logo',
                large_text='Gameloop Android Emulator',
                small_image=game_info['icon'],
                small_text=game_info['name'],
                start=int(self.gameloop_start_time) if self.gameloop_start_time else int(time.time())
            )
            return True
        except Exception as e:
            
            if "pipe" in str(e).lower() or "connection" in str(e).lower():
                self.log("Discord connection lost, attempting to reconnect...")
                self.discord_status.config(text="Reconnecting...", foreground="orange")
                
                if self.connect_discord():
                    
                    try:
                        state = "Idle" if self.is_idle() else "In Game"
                        self.discord_rpc.update(
                            details=game_info['name'],
                            state=state,
                            large_image='gameloop-logo',
                            large_text='Gameloop Android Emulator',
                            small_image=game_info['icon'],
                            small_text=game_info['name'],
                            start=int(self.gameloop_start_time) if self.gameloop_start_time else int(time.time())
                        )
                        return True
                    except Exception:
                        pass
            
            self.log(f"Discord update failed: {e}")
            return False
    
    def clear_presence(self):
        if self.discord_rpc:
            try:
                self.discord_rpc.clear()
            except:
                pass
    
    def monitor_loop(self):
        last_update = 0
        
        while self.running:
            try:
                current_time = time.time()
                gameloop_running = self.is_gameloop_running()
                
                
                self.gameloop_status.config(
                    text="Running" if gameloop_running else "Not Running",
                    foreground="green" if gameloop_running else "red"
                )
                
                if gameloop_running:
                    if self.gameloop_start_time is None:
                        self.gameloop_start_time = current_time
                        self.last_focus_time = current_time
                        self.log("Gameloop detected")
                    
                    
                    if self.is_gameloop_focused():
                        self.last_focus_time = current_time
                    
                    
                    current_package = self.get_current_app()
                    
                    if current_package:
                        game_info = self.get_game_info(current_package)
                        current_state = "Idle" if self.is_idle() else "In Game"
                        current_status_string = f"{game_info['name']} ({current_state})"
                        
                        
                        if (current_package != self.current_app or 
                            current_time - last_update > 30):
                            
                            
                            if self.current_status != current_status_string:
                                self.current_app = current_package
                                self.current_status = current_status_string
                                self.game_status.config(text=game_info['name'])
                                self.log(f"Playing: {current_status_string}")
                            
                            self.update_presence(game_info)
                            last_update = current_time
                
                else:
                    if self.current_app is not None:
                        self.log("Gameloop stopped")
                        self.current_app = None
                        self.current_status = None
                        self.gameloop_start_time = None
                        self.last_focus_time = None
                        self.game_status.config(text="None")
                        self.clear_presence()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.log(f"Monitor error: {e}")
                time.sleep(5)
    
    def start_monitoring(self, icon=None, item=None):
        if self.running:
            return
        
        if not self.connect_discord():
            messagebox.showerror("Error", "Failed to connect to Discord.\nMake sure Discord is running!")
            return
        
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.log("Monitoring started")
        
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.running = False
            self.monitor_thread.join(timeout=2)
        
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self, icon=None, item=None):
        self.running = False
        
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        if self.discord_rpc:
            try:
                self.discord_rpc.clear()
                self.discord_rpc.close()
                self.discord_rpc = None
            except:
                pass
        
        self.discord_status.config(text="Disconnected", foreground="red")
        self.gameloop_status.config(text="Not Running", foreground="red")
        self.game_status.config(text="None")
        self.current_app = None
        self.current_status = None
        self.log("Monitoring stopped")
    
    def run(self):
        self.root.mainloop()


def main():
    app = GameloopRPC()
    app.run()


if __name__ == "__main__":
    main()
