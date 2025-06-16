# This script requires the official Mistral AI and PyPDF2 libraries.
# If you encounter an ImportError, please install them by running:
# pip install mistralai PyPDF2

import os
import sys
import json
import time
from mistralai import Mistral
import PyPDF2

# --- Configuration ---

# Set your Mistral API key as an environment variable.
# Example: export MISTRAL_API_KEY="YOUR_MISTRAL_API_KEY_HERE"
API_KEY = os.getenv("MISTRAL_API_KEY")

# Set the input directory to 'personal'
INPUT_DIR = "personal"

# --- List of your personal files to process ---
# These files should be inside the INPUT_DIR folder.
FILES_TO_PROCESS = [
    "Masterthesis_GurhanCamgoz.pdf",
    "travelxx.pdf",
    "Gurhan_Camgoz_IDA_Portfolio.pdf",
    "Gurhan_Camgoz_MAS_Portfolio.pdf",
    "bookreview_gurhan_camgoz.pdf",
    "positionpaper_gurhan_camgoz.pdf",
]

# The final output file where all generated data will be appended.
OUTPUT_FILE_PATH = "output_dataset.jsonl"

# The Mistral model to use.
MODEL_NAME = "mistral-large-latest"


# --- Main Functions ---

def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a given PDF file.
    """
    if not os.path.exists(pdf_path):
        print(f"    - Warning: File not found at '{pdf_path}'. Skipping.")
        return None

    print(f"    - Reading text from '{pdf_path}'...")
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"    - Error reading PDF '{pdf_path}': {e}")
        return None


def get_system_prompt():
    """
    Creates the system prompt that defines the expert persona for the Mistral model.
    """
    return """
    You are an expert data creator for fine-tuning an ethnographic LLM. Your task is to transform the information and experiences described in anthropological and academic texts into multiple structured training examples.
    You MUST respond with only a valid JSON array of objects, starting with `[` and ending with `]`. Do not include any other text or explanations.
    """


def get_user_prompt(chunk_text):
    """
    Constructs the user-facing prompt for the Mistral API.
    """
    return f"""
    Thoroughly analyze the following text, which is a personal academic writing (e.g., a thesis, article, or field notes). Your goal is to convert the core ideas, arguments, and scenarios into structured training data for an AI that will act as a "digital colleague" for an ethnographer.

    Generate at least 5 and up to 15 high-quality, unique JSON examples based on the text.

    For each example, adhere to this JSON structure:
    {{
      "instruction": "<A varied and clear instructional phrase for the agent>",
      "spradley_type": "<'Descriptive', 'Structural', or 'Contrast'>",
      "context": "<A plausible statement from an ethnographer describing their work, a theoretical concept, or a fieldwork scenario from the text>",
      "output": "<An ideal, insightful question or reflection from the AI colleague that exemplifies the chosen spradley_type>"
    }}

    Rules for Generation:
    1. The `context` should capture the essence of an idea or situation from the source text, framed as if an ethnographer is discussing their work.
    2. The `spradley_type` MUST be one of only three values: "Descriptive", "Structural", or "Contrast".
    3. The `instruction` should be varied and creative.
    4. The `output` should be a thoughtful prompt that encourages reflexivity, deeper analysis, or methodological consideration.

    **Text to Process:**
    \"\"\"
    {chunk_text[:12000]}
    \"\"\"
    """


def generate_data_from_chunk(chunk_text, client):
    """
    Sends a chunk of text to the Mistral API and returns the generated data.
    """
    if not chunk_text or chunk_text.isspace():
        print("    - Skipping empty text chunk.")
        return None

    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(chunk_text)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            chat_response = client.chat.complete(
                model=MODEL_NAME,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            json_content = chat_response.choices[0].message.content
            return json.loads(json_content)
        except Exception as e:
            print(f"    - Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
            time.sleep(5)

    print("    - Failed to generate data after multiple retries.")
    return None


def main():
    """Main function to process a list of PDF files from a specified folder."""
    if not API_KEY:
        print("Error: MISTRAL_API_KEY environment variable not set.")
        sys.exit(1)

    client = Mistral(api_key=API_KEY)

    print(f"Starting data generation from {len(FILES_TO_PROCESS)} files in the '{INPUT_DIR}' directory.")
    print(f"Output will be appended to '{OUTPUT_FILE_PATH}'.\n")

    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as f_out:
        for filename in FILES_TO_PROCESS:
            # Construct the full path to the file inside the 'personal' directory
            full_path = os.path.join(INPUT_DIR, filename)

            print(f"--- Processing: {full_path} ---")

            text_chunk = extract_text_from_pdf(full_path)
            if not text_chunk:
                continue

            generated_data = generate_data_from_chunk(text_chunk, client)

            if generated_data and isinstance(generated_data, list):
                count = 0
                for item in generated_data:
                    if isinstance(item, dict) and all(
                            k in item for k in ["instruction", "spradley_type", "context", "output"]):
                        f_out.write(json.dumps(item, ensure_ascii=False) + '\n')
                        count += 1
                    else:
                        print(f"    - Skipping malformed item: {item}")
                print(f"    -> Successfully generated and appended {count} examples.")
            else:
                print(f"    -> Failed to generate valid data for '{filename}'.")

            # A brief pause to avoid hitting API rate limits
            time.sleep(1)

    print(f"\nProcessing complete. All generated data has been saved to '{OUTPUT_FILE_PATH}'.")


if __name__ == "__main__":
    main()
