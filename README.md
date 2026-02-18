# Moodle & YouTube Automation (JSON Generator)

## What does this project solve?
Feeding e-learning platforms (like Moodle) with dozens of YouTube videos can be an extremely manual, repetitive, and error-prone process. 

This project solves this pain point by automatically extracting data from a YouTube playlist and pairing it with the activity modules (H5P) previously created in Moodle. The script reads the source code (HTML) of both pages and cross-references the information, generating a standardized JSON file. This JSON serves as a reliable foundation for automation bots (like Playwright) to perform the final data entry on the platform.

## Security and Data Privacy
To ensure information security (private links, course data, internal IDs), **the extracted HTML files and the generated JSON are not committed to this repository**. 

They are globally mapped in our `.gitignore`:
- `**/*mapeadas.json`
- `**/*mdl.html`
- `**/*yt.html`

## Environment Setup

This project uses Python. We recommend using a Virtual Environment (venv) to isolate libraries.

1. **Create the venv:**
   In the terminal, at the project root, run:
   `python -m venv .venv`

2. **Activate the venv:**
   - **Linux/macOS:** `source .venv/bin/activate`
   - **Windows:** `.venv\Scripts\activate`

3. **Install dependencies:**
   With the venv activated, install the HTML parser **BeautifulSoup**:
   `pip install beautifulsoup4`

## Folder and File Structure

The script was designed to process courses modularly. Create a `content/` folder at the root of the project, and inside it, a subfolder for each course/module you intend to process.

**Structure example:**
```
project/
├── json_generate.py
└── content/
    └── data/
        ├── content.mdl.html
        └── content.yt.html
```

### Important rules for the subfolder:
1. Must contain **exactly one** Moodle file (`.mdl.html` extension).
2. Must contain **exactly one** YouTube file (`.yt.html` extension).

> **Flipped Playlists:** If the YouTube playlist is ordered from the last video to the first, simply add the extension `.flip` to the filename (e.g., `content.flip.yt.html`). The script will detect this and reverse the list automatically.

## How to run the JSON Generator

With the files correctly placed in the course subfolder and the `venv` activated, run the script passing the folder path as an argument:

`python json_generate.py content/data/`

### Result and Strict Validation
The script will perform a strict count. If the number of YouTube videos is **exactly equal** to the number of Moodle activities, it will generate the `mapping.json` file directly **inside the specified subfolder**, ready to be consumed by the automation bot. If the numbers don't match, the script will output an error alert and halt execution to prevent corrupted data.