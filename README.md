
# FCT Secure File Shredder 🛡️

A lightweight, GUI-based Python forensic tool designed to permanently and securely destroy files, folders, and wipe free disk space. 

When you normally delete a file, the operating system simply marks the space as available, leaving the actual data intact and easily recoverable by standard recovery tools. FCT Secure File Shredder prevents data recovery by overwriting the file's physical location with random bytes, obfuscating the filename, and permanently deleting it from the drive.

## 🚀 Features

* **Drag & Drop Support:** Easily drag files or entire folders into the application window to shred them.
* **Smart Algorithms (SSD & HDD):** * **1-Pass (Fast & Secure):** Optimized for SSDs.
  * **3-Pass (DoD 5220.22-M):** Designed for older mechanical HDDs.
* **Filename Obfuscation:** Renames files to random 15-character strings before deletion, ensuring original file names cannot be recovered from the File Allocation Table (FAT/MFT).
* **Windows Context Menu Integration:** Add the shredder to your Windows right-click menu with a single click inside the app.
* **Free Space Wiper:** Overwrites the empty space on your drive to permanently destroy previously "deleted" but still recoverable files.
* **Real-Time Progress:** Dynamic progress bar calculating accurate ETA and write speeds (MB/s).

## 🔬 Technical Note: SSD vs. HDD

This tool specifically separates algorithms for SSDs and HDDs based on modern storage mechanics:
* **Why 1-Pass for SSDs?** Modern Solid State Drives use *wear-leveling* and TRIM commands. Writing multiple passes (like the 3-pass DoD or 35-pass Gutmann method) on an SSD does not guarantee that the exact same physical memory cells are overwritten due to the SSD's internal controller. Furthermore, multiple passes will unnecessarily degrade your SSD's lifespan (TBW). A single pass of random data is scientifically sufficient to render the data unrecoverable.
* **Why 3-Pass for HDDs?** Mechanical hard drives retain magnetic remnants. The 3-Pass method (DoD 5220.22-M) overwrites data with zeros, ones, and then random bytes to ensure magnetic traces are completely destroyed.

## ⚙️ Prerequisites & Installation

1. Ensure you have **Python 3.x** installed.
2. Clone this repository:
```bash
   git clone [https://github.com/ferhatncgl/FCT-File-Shredder.git](https://github.com/ferhatncgl/FCT-File-Shredder.git)
   cd FCT-File-Shredder

```

3. Install the required Drag & Drop library (`tkinterdnd2`):
```bash
pip install tkinterdnd2

```


*(Note: If you have multiple Python versions, ensure you use the correct pip path, e.g., `python -m pip install tkinterdnd2`)*

## 🖥️ Usage

Run the application:

```bash
python main.py

```

1. Select your preferred shredding algorithm from the dropdown.
2. Drag and drop files/folders into the designated area, OR use the "Select File" / "Select Folder" buttons.
3. Confirm the permanent deletion warning.

**To use the Context Menu:** Click the "Add to Right-Click Menu" button. Now you can right-click any file in Windows File Explorer and select **Secure Delete (FCT)**.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK.** Files deleted using this tool cannot be recovered. The author is not responsible for any accidental data loss or hardware degradation caused by the "Wipe Free Space" feature.


