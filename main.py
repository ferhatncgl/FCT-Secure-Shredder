import os
import time
import random
import string
import threading
import shutil
import sys
import winreg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

class FCTShredderApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("FCT File Protector - Secure Shredder")
        self.geometry("500x450")
        self.resizable(False, False)
        
        self.is_processing = False
        self.thread = None
        
        self.setup_ui()
        self.check_context_menu_args()

    def setup_ui(self):
        # Header
        tk.Label(self, text="FCT Secure File Shredder", font=("Helvetica", 16, "bold")).pack(pady=(15, 5))
        tk.Label(self, text="Drag & Drop files/folders here or use the buttons below.", fg="gray").pack()

        # Method Selection
        frame_method = tk.Frame(self)
        frame_method.pack(pady=10)
        tk.Label(frame_method, text="Shredding Algorithm:").pack(side=tk.LEFT, padx=5)
        
        self.method_var = tk.StringVar(value="1-Pass (Fast & Secure - for SSD)")
        methods = ["1-Pass (Fast & Secure - for SSD)", "3-Pass (DoD 5220.22-M - for HDD)"]
        self.method_dropdown = ttk.Combobox(frame_method, textvariable=self.method_var, values=methods, state="readonly", width=35)
        self.method_dropdown.pack(side=tk.LEFT)

        # Drag & Drop Area
        self.drop_area = tk.Label(self, text="[ DROP FILES OR FOLDERS HERE ]", bg="#2c3e50", fg="white", font=("Helvetica", 12), width=45, height=5, relief="groove")
        self.drop_area.pack(pady=15)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.handle_drop)

        # Buttons
        frame_btns = tk.Frame(self)
        frame_btns.pack(pady=5)
        tk.Button(frame_btns, text="Select File", command=self.select_file, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="Select Folder", command=self.select_folder, width=15).pack(side=tk.LEFT, padx=5)
        
        # Tools
        frame_tools = tk.Frame(self)
        frame_tools.pack(pady=10)
        tk.Button(frame_tools, text="Wipe Free Space (Warning)", command=self.wipe_free_space_warning, bg="#f0ad4e", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_tools, text="Add to Right-Click Menu", command=self.install_context_menu, bg="#5bc0de", fg="white").pack(side=tk.LEFT, padx=5)

        # Progress Area
        self.lbl_status = tk.Label(self, text="Ready.", font=("Helvetica", 10), fg="blue")
        self.lbl_status.pack(pady=(15, 0))
        
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5)
        
        self.lbl_eta = tk.Label(self, text="ETA: --:-- | Speed: -- KB/s", font=("Helvetica", 9), fg="gray")
        self.lbl_eta.pack()

        # Footer
        tk.Label(self, text="Developed by ferhatncgl", font=("Helvetica", 8, "italic"), fg="#7f8c8d").pack(side=tk.BOTTOM, pady=10)

    def handle_drop(self, event):
        if self.is_processing: return
        paths = self.split_dnd_paths(event.data)
        self.start_processing(paths)

    def split_dnd_paths(self, data):
        # tkinterdnd2 returns paths as a space-separated string, sometimes wrapped in curly braces
        import re
        return re.findall(r'\{.*?\}|\S+', data)

    def select_file(self):
        if self.is_processing: return
        filepaths = filedialog.askopenfilenames(title="Select Files to Hard Delete")
        if filepaths:
            self.start_processing(filepaths)

    def select_folder(self):
        if self.is_processing: return
        folderpath = filedialog.askdirectory(title="Select Folder to Hard Delete")
        if folderpath:
            self.start_processing([folderpath])

    def get_passes(self):
        val = self.method_var.get()
        if "3-Pass" in val: return 3
        return 1

    def start_processing(self, paths):
        paths = [p.strip('{}') for p in paths] # Clean DND artifacts
        
        msg = f"Are you sure you want to PERMANENTLY destroy {len(paths)} item(s)?\nThis cannot be undone!"
        if not messagebox.askyesno("Warning", msg, icon='warning'):
            return

        self.is_processing = True
        self.disable_ui()
        passes = self.get_passes()
        
        self.thread = threading.Thread(target=self.process_items, args=(paths, passes), daemon=True)
        self.thread.start()

    def process_items(self, paths, passes):
        all_files = []
        for path in paths:
            if os.path.isfile(path):
                all_files.append(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        all_files.append(os.path.join(root, f))
        
        total_bytes = sum(os.path.getsize(f) for f in all_files if os.path.exists(f))
        bytes_processed = 0
        start_time = time.time()

        for idx, filepath in enumerate(all_files):
            if not os.path.exists(filepath): continue
            
            file_size = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            try:
                with open(filepath, "ba+") as file:
                    for p in range(passes):
                        file.seek(0)
                        
                        # Generate data based on pass type
                        if passes == 3 and p == 0: data_chunk = b'\x00' * 4096
                        elif passes == 3 and p == 1: data_chunk = b'\xff' * 4096
                        else: data_chunk = os.urandom(4096)
                        
                        written_for_file = 0
                        while written_for_file < file_size:
                            chunk_size = min(4096, file_size - written_for_file)
                            file.write(data_chunk[:chunk_size])
                            written_for_file += chunk_size
                            
                            if p == passes - 1: # Only update progress on the last pass
                                bytes_processed += chunk_size
                                self.update_progress(bytes_processed, total_bytes, start_time, filename)
                
                # Rename and delete
                dir_name = os.path.dirname(filepath)
                random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
                new_path = os.path.join(dir_name, random_name)
                os.rename(filepath, new_path)
                os.remove(new_path)
                
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

        # Try to remove empty folders if a directory was dropped
        for path in paths:
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except:
                    pass

        self.finish_processing()

    def update_progress(self, processed, total, start_time, current_file):
        if total == 0: return
        percent = (processed / total) * 100
        elapsed = time.time() - start_time
        
        speed_bps = processed / elapsed if elapsed > 0 else 0
        speed_mbps = speed_bps / (1024 * 1024)
        
        remaining_bytes = total - processed
        eta_seconds = remaining_bytes / speed_bps if speed_bps > 0 else 0
        
        mins, secs = divmod(int(eta_seconds), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        self.after(0, self._set_ui_progress, percent, time_str, speed_mbps, current_file)

    def _set_ui_progress(self, percent, time_str, speed_mbps, current_file):
        self.progress_bar["value"] = percent
        self.lbl_status.config(text=f"Shredding: {current_file[:30]}... ({percent:.1f}%)")
        self.lbl_eta.config(text=f"ETA: {time_str} | Speed: {speed_mbps:.2f} MB/s | Active: {'/' if int(time.time()*2)%2==0 else '\\'}")

    def finish_processing(self):
        self.after(0, self._reset_ui)
        messagebox.showinfo("Complete", "Selected items have been securely destroyed.")

    def _reset_ui(self):
        self.is_processing = False
        self.progress_bar["value"] = 0
        self.lbl_status.config(text="Ready.")
        self.lbl_eta.config(text="ETA: --:-- | Speed: -- MB/s")
        self.enable_ui()

    def disable_ui(self):
        self.method_dropdown.config(state="disabled")
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, tk.Button):
                        btn.config(state="disabled")

    def enable_ui(self):
        self.method_dropdown.config(state="readonly")
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, tk.Button):
                        btn.config(state="normal")

    def wipe_free_space_warning(self):
        msg = ("WARNING: This will fill your entire drive with random data to overwrite previously deleted files.\n\n"
               "This is extremely slow, will temporarily consume ALL free disk space, and degrades SSD lifespan.\n\n"
               "Do you want to proceed?")
        if messagebox.askyesno("Free Space Wiper", msg, icon='warning'):
            self.is_processing = True
            self.disable_ui()
            threading.Thread(target=self.wipe_free_space_task, daemon=True).start()

    def wipe_free_space_task(self):
        temp_file = os.path.join(os.getcwd(), "fct_wipe_temp.tmp")
        self.after(0, lambda: self.lbl_status.config(text="Writing garbage data to free space... Please wait."))
        try:
            with open(temp_file, "wb") as f:
                while True:
                    f.write(os.urandom(1024 * 1024 * 10)) # 10MB chunks
                    self.after(0, lambda: self.lbl_eta.config(text=f"Filling disk... Active: {'/' if int(time.time()*2)%2==0 else '\\'}"))
        except OSError:
            # Disk is full
            pass
        finally:
            self.after(0, lambda: self.lbl_status.config(text="Disk full. Deleting garbage data..."))
            if os.path.exists(temp_file):
                os.remove(temp_file)
            self.after(0, self._reset_ui)
            messagebox.showinfo("Complete", "Free space has been securely wiped.")

    def install_context_menu(self):
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            
            # Using HKEY_CURRENT_USER avoids needing Run As Administrator
            key_path = r"Software\Classes\*\shell\FCT_Shredder"
            command_path = rf"{key_path}\command"
            
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValue(key, "", winreg.REG_SZ, "Secure Delete (FCT)")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, "imageres.dll,-5302") 
            winreg.CloseKey(key)
            
            cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_path)
            winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'{exe_path} "%1"')
            winreg.CloseKey(cmd_key)
            
            messagebox.showinfo("Success", "Added to Right-Click Menu successfully.")
        except Exception as e:
            messagebox.showerror("Registry Error", f"Failed to add context menu: {e}")

    def check_context_menu_args(self):
        if len(sys.argv) > 1:
            target = sys.argv[1]
            if os.path.exists(target):
                self.after(500, lambda: self.start_processing([target]))

if __name__ == "__main__":
    app = FCTShredderApp()
    app.mainloop()