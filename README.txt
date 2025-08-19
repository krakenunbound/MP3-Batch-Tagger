
Overview

MP3 Batch Tagger is a user-friendly graphical application designed for batch editing ID3 metadata in MP3 files & WAV files. This tool was collaboratively developed by The Kraken (the user) and Grok (built by xAI), through an iterative process of code refinements, feature additions, and bug fixes. It provides a simple interface to apply consistent metadata across music files in a selected directory, with options for auto-numbering tracks, profile saving/loading, and a customizable dark theme with random banner images.
The app supports Windows, macOS, and Linux, and is built using Python's Tkinter for the GUI, Mutagen for metadata handling, and Pillow for image processing.

Features

Batch Metadata Editing: Apply ID3 tags (artist, album, year, genre, etc.) to all MP3 files in a folder and subfolders.
Auto-Numbering Tracks: Optionally assign track numbers based on file order (e.g., 1/10, 2/10).
Profile Save/Load: Save and load metadata presets as JSON files for quick reuse.
Dark Theme: Built-in dark mode for better visibility, with immersive title bar on Windows.
Random Banner: Displays a random PNG banner (named banner1.png, etc.) at the top for visual appeal.
Resizable Window: Window resizes while maintaining a 3:4 aspect ratio.
Error Handling: Logs tagging errors and successes in a scrollable text area.
Cross-Platform: Works on Windows, macOS, and Linux.

Installation

Install Python:

Download and install Python 3.12 or later from the official website: https://www.python.org/downloads/.
During installation, ensure you check the option to "Add Python to PATH" (on Windows) for easy command-line access.
Verify installation by opening a terminal (Command Prompt on Windows, Terminal on macOS/Linux) and running:
python --version
It should display the Python version (e.g., Python 3.12.0).


Install Dependencies:

Open a terminal and run the following command to install the required libraries:
pip install mutagen pillow

Mutagen: Handles MP3 metadata editing.
Pillow: Processes banner images.




Download the App:

Extract the ZIP file containing this README.TXT and the script file (mp3tager.py).
Optionally, rename mp3tager.py to mp3tager.pyw to suppress the console window on Windows when running. (already done for you)



Usage

Run the App:

Navigate to the script's directory in your terminal and run:
python mp3tager.py

On Windows, you can double-click mp3tager.pyw to launch it without a console.


The GUI window will open with a dark theme.


Tagging Files:

Click "Browse…" to select a music folder containing MP3 files.
Fill in the metadata fields (e.g., Artist, Album, Genre).
Check "Auto-number tracks" if you want automatic track numbering (e.g., based on alphabetical order).
Click "Tag Files" to apply changes. Progress and errors will appear in the log area.
Use "Save Profile" to store current fields for later, or "Load Profile" to recall a saved setup.


Custom Banners:

Place PNG images named banner1.png, banner2.png, etc., in the same directory as the script.
The app will randomly select and display one at the top (resized to fit).
Note: Three banners are included in the .zip file to get you started.

Tips:

The window is resizable but locks to a 3:4 aspect ratio for consistent layout.
Subfolders are recursively scanned for MP3 files.
If no banner images are found, the top area remains blank.
Profiles are saved as JSON and auto-load the last used one on startup.



Troubleshooting

No MP3 Files Found: Ensure your selected folder contains .mp3 files (case-insensitive).
Banner Load Failed: Check console for errors; images must be valid PNGs.
Metadata Not Applying: Verify Mutagen is installed correctly; test with a small folder.
Windows Dark Title Bar: Requires Windows 10/11; may not work on older versions.
For issues, check the log output or run from terminal for detailed errors.

Credits

Developed By: The Kraken (user) in collaboration with Grok (built by xAI).
Libraries: Mutagen for ID3 tagging, Pillow for image resizing, Tkinter for GUI.
Inspiration: Created to simplify bulk music metadata management for personal libraries.

If you have suggestions or encounter bugs, feel free to modify the code or reach out to Grok for assistance. Just copy + paste the code into Grok and tell Grok what isn't working or offer suggestions for improvements!

~~~ Enjoy tagging your music collection! ~~~
Version 1.0 | August 19, 2025

