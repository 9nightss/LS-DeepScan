# LS-DeepScan
🔍 Project LS – Deep Scan Port

A powerful local file scanner with a sleek customtkinter GUI, designed to recursively search through your drives for specific strings within common file formats. Ideal for forensic review, lost file tracing, debugging, or deep system audits.
🚀 Features

    Admin Privilege Check: Automatically requests elevation for deeper access.

    Drive Scanning: Supports scanning just the C:// drive or all connected drives.

    File Content Search: Searches within a wide range of file types (text, code, media, etc.).

    Preview Toggle: Optionally enable future content preview functionality.

    Real-Time Progress Tracking: Progress bar with percentage feedback.

    Live Logging: Errors are timestamped, categorized, and displayed in a sortable tree.

    File Exclusion: Skips C:\Windows for speed and to avoid noise.

    Double-Click to Open: Easily open files or folders from results.

🛠️ Tech Stack

    Python 3.10+

    customtkinter for UI

    ctypes for privilege management

    csv and threading for logging and performance

📦 Installation

    Clone the repo:

git clone https://github.com/yourusername/project-ls-deepscan.git
cd project-ls-deepscan

Install required packages:

pip install customtkinter

Run the app (with Admin privileges):

    python deep_scan.py

🖥️ Supported File Types

.txt, .docx, .xlsx, .csv, .log, .md, .xml, .html, .htm,
.mp3, .mp4, .wav, .jpg, .png, .json, .py, .js, .java,
.cpp, .cs, .rb, .php, .sql

    You can customize these by editing the self.target_extensions list in the ScanThread class.

📁 Logs

Errors are saved in scan_errors.csv (same directory as the script) with:

    Timestamp

    Error Code

    File Name

    File Path

Error codes:

    100 - Permission Denied

    101 - File Not Found

    102 - Unsupported Encoding

    105 - Other Exceptions

⚠️ Notes

    Due to OS limitations, the progress bar may cap at ~98-99% due to excluded system folders.

    Currently optimized for Windows. Linux/macOS support is possible with small tweaks (encoding handling + file opener).

    Future features (like content previews) are already scaffolded in the code.

👀 Screenshot

    You can drop in a screenshot here later showing the GUI in action.

📃 License

MIT License — use it, fork it, break it, improve it.
