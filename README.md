
# Round1A – Document Processing with Docker

This repository contains a Python-based solution to process PDF documents into structured JSON format. The entire solution is designed to run inside a secure, network-isolated Docker container.

---

## Project Structure

```
Round1A/
├── input/         # Input folder – place your 5 PDF files here
├── output/        # Output folder – generated JSON files will appear here
├── app/round1a.py # Main processing script
├── Dockerfile     # Docker build file
└── README.md      # Project documentation
```

---

## Getting Started

### 1. Prerequisites

- Docker installed on your system
- PDF files ready for processing

---

## Instructions

### Step 1: Add Input Files

Place **exactly 5 PDF files** inside the `input/` directory before running the container.

---

### Step 2: Build the Docker Image

From the root of the project directory, run:

```bash
docker build -t mysolutionname:somerandomidentifier .
```

> Replace `mysolutionname` and `somerandomidentifier` with your own tag if needed.

---

### Step 3: Run the Docker Container

```bash
docker run --rm \
  -v "${PWD}/input:/app/input" \
  -v "${PWD}/output:/app/output" \
  --network none \
  mysolutionname:somerandomidentifier
```

-  `--rm` removes the container after execution
-  `-v` mounts the input/output directories
-  `--network none` disables network access

---

## Output Format

For each PDF in `input/`, a corresponding `.json` file will be generated in `output/`. Each JSON file contains the structured extraction of the document's content.

---

## Sample Test

You may test using dummy PDFs:

Make sure they are placed in the `input/` directory before running.

---

## Notes

- Do **not** run without PDF files in the `input/` directory.
- Output files will **only** be created if valid PDFs are present.
- The script will skip processing if no files are detected.

```
