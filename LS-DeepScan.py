import os
import sys
import ctypes
import datetime
import csv
import webbrowser
import customtkinter
from tkinter import filedialog
import threading
from tkinter import ttk  # Added missing import

# -------------------- Admin Check -------------------- #
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

# -------------------- Scan Worker Thread -------------------- #
class ScanThread(threading.Thread):
    def __init__(self, root_dir, encodings, search_query, app):
        super().__init__()
        self.root_dir = root_dir
        self.encodings = encodings
        self.search_query = search_query.lower()
        self.app = app
        self.excluded = ['C:\\Windows'] # because we dont need to scan it on most of the cases 
        
        # i used most of the text/media based files but feel free to change or add new extentions
        self.target_extensions = [
            ".txt", ".docx", ".xlsx", ".csv", ".log", ".md",
            ".xml", ".html", ".htm", ".mp3", ".mp4", ".wav", ".jpg", ".png", ".json",
            ".py", ".js", ".java", ".cpp", ".cs", ".rb", ".php", ".sql"
        ]

    def run(self):
        self.app.set_status_scanning()
        total_files = 0
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            if any(ex in dirpath for ex in self.excluded):
                continue
            total_files += len(filenames)

        scanned_files = 0
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            if any(ex in dirpath for ex in self.excluded):
                continue
            for file in filenames:
                filepath = os.path.join(dirpath, file)
                scanned_files += 1
                try:
                    if not any(file.lower().endswith(ext) for ext in self.target_extensions):
                        continue

                    with open(filepath, 'rb') as f:
                        data = f.read()

                    content = None
                    for enc in self.encodings:
                        try:
                            content = data.decode(enc)
                            break
                        except:
                            continue

                    if content:
                        if file.lower().endswith(".sql"):
                            lowered = content.lower()
                            if any(word in lowered for word in ["microsoft", "windows", "apple"]):
                                continue

                        if self.search_query in file.lower() or self.search_query in content.lower():
                            self.app.display_result(filepath)
                    else:
                        self.app.log_error(filepath, "Unsupported Encoding", 102)
                except PermissionError:
                    self.app.log_error(filepath, "Permission Denied", 100, "red")
                except FileNotFoundError:
                    self.app.log_error(filepath, "File Not Found", 101)
                except Exception as e:
                    self.app.log_error(filepath, str(e), 105)
                self.app.update_progress(scanned_files, total_files)

        self.app.set_status_standby()
        self.app.update_progress(1, 1)  # Force 100%

# -------------------- Main GUI -------------------- #
class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project LS- Deep Scan Port")
        self.root.geometry("1200x600")
        self.root.configure(bg="#1e1e1e")
        self.log_file = "scan_errors.csv" #its gonna be on the same folder as the program
        self.init_ui()

    def init_ui(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        self.main_pane = customtkinter.CTkFrame(self.root)
        self.main_pane.pack(fill="both", expand=True)

        self.side_panel = customtkinter.CTkFrame(self.main_pane, width=200)
        self.side_panel.pack(side="left", fill="y")
        customtkinter.CTkLabel(self.side_panel, text="Options:").pack(pady=10)
        self.side_panel.pack(padx=10, pady=5)

        self.right_panel = customtkinter.CTkFrame(self.main_pane)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.top_frame = customtkinter.CTkFrame(self.right_panel, fg_color="#1e1e1e")
        self.top_frame.pack(fill="x", padx=10, pady=5)

        self.search_entry = customtkinter.CTkEntry(self.top_frame, width=300)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.start_scan())

        self.search_btn = customtkinter.CTkButton(self.top_frame, text="Search", command=self.start_scan)
        self.search_btn.pack(side="left", padx=5)

        self.preview_var = customtkinter.StringVar(value="off")
        self.drive_mode = customtkinter.StringVar(value="C")
        self.toggle_drives = customtkinter.CTkSwitch(self.side_panel, text="All Drives", variable=self.drive_mode, onvalue="ALL", offvalue="C")
        self.toggle_drives.pack(pady=10)

        self.preview_toggle = customtkinter.CTkSwitch(self.side_panel, text="Enable Preview", variable=self.preview_var,
                                                      onvalue="on", offvalue="off")
        self.preview_toggle.pack(pady=10, fill="x")

        #Engin add something here!

        # self.heavy_var = customtkinter.StringVar(value="off")
        # self.heavy_toggle = customtkinter.CTkSwitch(self.side_panel, text="[Future Feature]", variable=self.heavy_var, 
        #                                           onvalue="on", offvalue="off")
        # self.heavy_toggle.pack(pady=10, fill="x")

        self.status_and_progress = customtkinter.CTkFrame(self.right_panel, fg_color="#1e1e1e")
        self.status_and_progress.pack(fill="x", padx=10, pady=5)

        #FIX IT: There is a bug on windows progress bar is stuck on 98 - 99 because of the excluded folder even if the scanning proccess is done..
        self.progress = customtkinter.CTkProgressBar(self.status_and_progress, orientation="horizontal")
        self.progress.set(0)
        self.progress.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.status_dot = customtkinter.CTkCanvas(self.status_and_progress, width=20, height=20, bg="#1e1e1e", highlightthickness=0)
        self.status = self.status_dot.create_oval(5, 5, 15, 15, fill="red")
        self.status_dot.pack(side="left", padx=5)

        self.percentage_label = customtkinter.CTkLabel(self.right_panel, text="0%")
        self.percentage_label.pack()

        self.result_list = customtkinter.CTkTextbox(self.right_panel)
        self.result_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.result_list.bind('<Double-Button-1>', self.open_file_or_folder)

        self.log_tree = customtkinter.CTkFrame(self.right_panel, fg_color="#1e1e1e")
        self.log_tree.pack(fill="both", expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        bordercolor="#2b2b2b",
                        borderwidth=0,
                        font=('Segoe UI', 10))
        style.map('Treeview', background=[('selected', '#347083')])
        
                
        self.tree = ttk.Treeview(self.log_tree, columns=("date", "code", "file", "path"), show="headings")
        self.tree.heading("date", text="Date")
        self.tree.heading("code", text="Code")
        self.tree.heading("file", text="File")
        self.tree.heading("path", text="Path")
        self.tree.pack(fill="both", expand=True)


    # this function mostly calls for different file formats if user runs on different os or any linux distros..

    def start_scan(self):
        encodings = ["utf-8", "utf-32", "iso-8859-1", "ascii", "ansi", "oem", "macintosh", "cp437", "cp850"]
        query = self.search_entry.get().strip()
        if not query:
            return

        self.result_list.delete("1.0", "end")
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Sole purpose of this is bug finding and fixing later for different sections and errors if it occur 

        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Error Code", "File Name", "Path"])

        scan_thread = ScanThread("C://", encodings, query, self)
        scan_thread.start()

    def update_progress(self, current, total):
        percent = int(current / total * 100)
        self.progress.set(percent / 100)
        self.percentage_label.configure(text=f"{percent}%")

    def display_result(self, path):
        self.result_list.insert("end", os.path.basename(path) + " — " + path + "\n")

    def open_file_or_folder(self, event):
        try:
            index = self.result_list.index("insert")
            line = self.result_list.get(index + ".0", index + ".end").strip()
            path = line.split(" — ")[-1]
            if os.path.exists(path):
                os.startfile(path)
        except Exception:
            pass

    def log_error(self, path, message, code, color=None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file = os.path.basename(path)
        self.tree.insert("", "end", values=(timestamp, code, file, path))
        if color == "red":
            last = self.tree.get_children()[-1]
            self.tree.tag_configure('red', foreground='red')
            self.tree.item(last, tags=('red',))
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, code, file, path])

        #im just lazy 

    def set_status_scanning(self):
        self.status_dot.itemconfig(self.status, fill="green")

    def set_status_standby(self):
        self.status_dot.itemconfig(self.status, fill="red")

# -------------------- Entry Point -------------------- #
if __name__ == '__main__':
    root = customtkinter.CTk()
    app = SearchApp(root)
    root.mainloop()
