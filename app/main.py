# round1a.py
import os
import fitz  # PyMuPDF
import json
import re
import unicodedata
from collections import defaultdict
from jsonschema import validate, ValidationError


def is_valid_heading(text):
    return not re.match(r"^0\\.|^\\d+\\.?$", text.strip()) and len(text.strip()) > 3

def clean_text(text):
    normalized = unicodedata.normalize("NFKD", text)
    cleaned = re.sub(r'(.)\\1{2,}', r'\\1', normalized)
    cleaned = re.sub(r'\\s+', ' ', cleaned).strip()
    return cleaned

def split_numbered_sections(text):
    # Split into top-level numbered sections (e.g., 1., 2.) and subpoints like (a), (b)
    primary_sections = re.split(r"(?=\\n?\\d+\\.\\s)", text)
    results = []
    seen = set()
    for sec in primary_sections:
        sub_splits = re.split(r"(?=\\(\\w\\)\\s)", sec)
        for s in sub_splits:
            cleaned = s.strip()
            if cleaned and is_valid_heading(cleaned) and cleaned not in seen:
                seen.add(cleaned)
                results.append(cleaned)
    return results

def extract_headings(doc):
    headings = []
    font_sizes = defaultdict(int)
    grouped_text_by_size = defaultdict(list)
    seen_texts = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = clean_text(span["text"].strip())
                        size = span["size"]
                        if text:
                            font_sizes[size] += 1
                            grouped_text_by_size[(size, page_num)].append(text)

    sizes_sorted = sorted(font_sizes.keys(), reverse=True)
    h1_size = sizes_sorted[0]
    h2_size = sizes_sorted[1] if len(sizes_sorted) > 1 else h1_size - 1
    h3_size = sizes_sorted[2] if len(sizes_sorted) > 2 else h2_size - 1
    h4_size = sizes_sorted[3] if len(sizes_sorted) > 3 else h3_size - 1
    h5_size = sizes_sorted[4] if len(sizes_sorted) > 4 else h4_size - 1

    title = ""
    for (size, page), texts in grouped_text_by_size.items():
        merged_text = " ".join(texts).strip()
        if not is_valid_heading(merged_text):
            continue

        if size == h1_size:
            if not title:
                title = merged_text
            headings.append({"level": "H1", "text": merged_text, "page": page + 1})

        elif size == h2_size:
            for section in split_numbered_sections(merged_text):
                if section not in seen_texts:
                    headings.append({"level": "H2", "text": section, "page": page + 1})
                    seen_texts.add(section)

        elif size == h3_size:
            for section in split_numbered_sections(merged_text):
                if section not in seen_texts:
                    headings.append({"level": "H3", "text": section, "page": page + 1})
                    seen_texts.add(section)

        elif size == h4_size:
            for section in split_numbered_sections(merged_text):
                if section not in seen_texts:
                    headings.append({"level": "H4", "text": section, "page": page + 1})
                    seen_texts.add(section)
    
        elif size == h5_size:
            for section in split_numbered_sections(merged_text):
                if section not in seen_texts:
                    headings.append({"level": "H5", "text": section, "page": page + 1})
                    seen_texts.add(section)

    return title, headings

def process_pdf(filepath):
    doc = fitz.open(filepath)
    title, outline = extract_headings(doc)
    return {"title": title, "outline": outline}

def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    outline_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "outline": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "string"},
                        "text": {"type": "string"},
                        "page": {"type": "integer"}
                    },
                    "required": ["level", "text", "page"]
                }
            }
        },
        "required": ["title", "outline"]
    }

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            result = process_pdf(input_path)

            try:
                validate(instance=result, schema=outline_schema)
                with open(output_path, "w") as f:
                    json.dump(result, f, indent=2)
            except ValidationError as e:
                print(f"Validation error in {filename}: {e.message}")


if __name__ == "__main__":
    main()
