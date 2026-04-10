# STEP to OBJ Converter

A web application that converts CAD files in STEP format (.step, .stp) to Wavefront OBJ mesh files.

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000 in your browser.

## Features

- Drag-and-drop file upload
- STEP to OBJ conversion powered by OpenCASCADE (via cascadio)
- Interactive 3D preview using Three.js
- One-click OBJ download
- Reports vertex/face count and file size

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`
