import os
import re
import PyPDF2

# --- Configuration ---

# Input PDF file name
PDF_FILE_PATH = "Masterthesis_GurhanCamgoz.pdf"

# The directory where the output text files for each subsection will be saved.
OUTPUT_DIR = "thesis_subsections"


# --- Main Functions ---

def extract_full_text(pdf_path):
    """
    Extracts all text from the PDF into a single string.
    """
    print(f"Reading full text from '{pdf_path}'...")
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            full_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        print("Successfully extracted full text.")
        return full_text
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return None


def clean_text(text):
    """
    Cleans the extracted text by removing isolated page numbers and extra whitespace.
    """
    # This regex finds lines that likely contain only a page number (and maybe whitespace)
    # and removes them, which helps stitch paragraphs back together correctly.
    cleaned_text = re.sub(r'\n\s*\d+\s*\n', '\n\n', text, flags=re.UNICODE)
    # Consolidate multiple newlines into a standard paragraph break
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    return cleaned_text


def split_text_by_subsections(full_text):
    """
    Splits the full text into chunks based on a predefined list of subsection titles
    using a robust regex splitting method.

    Args:
        full_text (str): The entire text content of the thesis.

    Returns:
        A dictionary where keys are sanitized subsection titles and values are the text chunks.
    """
    print("Dynamically splitting text based on a list of known subsection headers...")

    # A definitive list of subsection titles from the thesis index.
    # Using a list ensures the correct order.
    subsection_titles = [
        "0x0. An Introduction",
        "0x1. A Miniature Conceptual History of Earthquakes",
        "0x2. A Non-Dwelling Perspective",
        "0x3. A Secret Echo",
        "1x0. From Canonical Formula to Inverted Ethnography",
        "1x1. From Ethnographic Present to Third-Person’s Perspective",
        "1x2. From Self-Resonance to Fractal Identity",
        "1x3. From Measurement to Decoherence",
        "2x0. Axiom and Method",
        "2x1. Biography of an Ordinary Anthropologist",
        "2x2. Life in Disaster Housing Projects",
        "2x3. Islamic Make-up and ‘Cat Bonds’",
        "3x0. Dialogue with the Neighbours of the Inside",
        "3x1. Swinging from a Hilltop in Athens",
        "3x2. Pangaea of our Common Dreams-Nightmares",
        "3x3. Epilogue/Postscript on the Emergent Human-Science"
    ]

    # Escape special regex characters (like '.') in titles and join with OR operator '|'
    # This creates a single pattern to find any of the titles.
    pattern_str = "|".join([re.escape(title) for title in subsection_titles])

    # The capturing group () makes re.split keep the delimiters (the titles) in the results.
    pattern = re.compile(f'({pattern_str})')

    # Split the text by the titles.
    # The result is: [text_before_first_title, title1, text1, title2, text2, ...]
    parts = pattern.split(full_text)

    if len(parts) <= 1:
        print("Warning: Could not split text. No titles found.")
        return {}

    subsections = {}
    # The list is structured as [intro_junk, title_1, content_1, title_2, content_2, ...]
    # We iterate through the list in pairs of (title, content), starting from the first title.
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        # The content is the next item in the list, if it exists.
        if i + 1 < len(parts):
            content = parts[i + 1].strip()

            # Sanitize title for filename.
            safe_title = re.sub(r'[\\/*?:"<>|.\s’]', "_", title)
            subsections[safe_title] = content
            print(f"  - Found and extracted subsection: '{title}'")
        else:
            print(f"  - Found title '{title}' but no subsequent content.")

    # Special handling for the final subsection to trim the Bibliography.
    last_title = subsection_titles[-1]
    last_safe_title = re.sub(r'[\\/*?:"<>|.\s’]', "_", last_title)
    if last_safe_title in subsections:
        text = subsections[last_safe_title]
        try:
            bib_index = text.lower().find("bibliography")
            if bib_index != -1:
                subsections[last_safe_title] = text[:bib_index].strip()
                print(f"  - Trimmed last section at 'Bibliography'.")
        except ValueError:
            pass  # Bibliography not found, keep the whole chunk.

    print(f"\nSuccessfully split the text into {len(subsections)} subsections.")
    return subsections


def main():
    """Main function to split the thesis PDF into subsection-based text files."""
    full_text_raw = extract_full_text(PDF_FILE_PATH)
    if not full_text_raw:
        return

    # Clean the text before splitting
    full_text_cleaned = clean_text(full_text_raw)

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: '{OUTPUT_DIR}'")

    subsection_chunks = split_text_by_subsections(full_text_cleaned)

    if not subsection_chunks:
        print("No subsections were extracted. Exiting.")
        return

    print("\nSaving subsections to individual files...")
    for safe_title, text in subsection_chunks.items():
        if not text.strip():
            print(f"  - Skipping empty subsection: '{safe_title}'")
            continue

        filename = f"{safe_title}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  - Saved '{filepath}'")

    print(f"\nProcessing complete. All thesis subsections have been saved in the '{OUTPUT_DIR}' folder.")


if __name__ == "__main__":
    main()
