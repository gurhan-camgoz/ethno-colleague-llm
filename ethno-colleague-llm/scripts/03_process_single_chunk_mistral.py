import os
import sys
import json
import time
from mistralai import Mistral

# --- Configuration ---
API_KEY = os.getenv("MISTRAL_API_KEY")
INPUT_DIR = "chapter_chunks"
OUTPUT_FILE_PATH = "output_dataset.jsonl"
MODEL_NAME = "mistral-large-latest"

def clean_json_response(response_content):
    """
    Cleans the response content by removing markdown formatting and other non-JSON elements.

    Args:
        response_content (str): The raw content from the API response

    Returns:
        str: Cleaned JSON string
    """
    # Remove markdown code block markers if present
    content = response_content.strip()

    # Remove ```json from the start if present
    if content.startswith('```json'):
        content = content[7:].strip()  # Remove '```json' and any following whitespace
    elif content.startswith('```'):
        content = content[3:].strip()  # Just remove backticks if no 'json' specifier

    # Remove closing backticks if present
    if content.endswith('```'):
        content = content[:-3].strip()

    return content

def get_system_prompt():
    return """
    You are an expert data creator for fine-tuning an ethnographic LLM. Your task is to transform the information and experiences described in anthropological texts into multiple structured training examples.
    You MUST respond with only a valid JSON array of objects, starting with `[` and ending with `]`. Do not include any other text, explanations, or markdown formatting.
    """

def get_user_prompt(chunk_text):
    return f"""
    Thoroughly analyze the following text, which is a chapter from an anthropological reader. Generate at least 5 and up to 15 high-quality, unique JSON examples based on the text.

    For each example you create, you MUST adhere strictly to the following JSON structure:
    {{
      "instruction": "<A varied and clear instructional phrase for the agent>",
      "spradley_type": "<'Descriptive', 'Structural', or 'Contrast'>",
      "context": "<A plausible participant's statement or a concise summary of an ethnographic scenario based on the text>",
      "output": "<An ideal, insightful, and open-ended question the agent should ask, which perfectly exemplifies the chosen spradley_type>"
    }}

    Rules for Generation:
    1. The `context` should feel authentic to a fieldwork situation described or implied in the text.
    2. The `spradley_type` MUST be one of only three values: "Descriptive", "Structural", or "Contrast".
    3. The `instruction` should be varied for each example to teach the model flexibility.
    4. The `output` question must be insightful and directly reflect the function of the chosen `spradley_type`.
    5. Respond ONLY with the JSON array, no additional text, explanations, or formatting.

    **Text to Process:**
    \"\"\"
    {chunk_text[:12000]}
    \"\"\"
    """

def generate_data_from_chunk(chunk_text, client):
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
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Get the raw response content
            raw_content = chat_response.choices[0].message.content

            # Clean the content to extract only the JSON part
            clean_content = clean_json_response(raw_content)

            # Debug output - print the cleaned content to verify
            print("Cleaned content:", clean_content[:200])  # Print first 200 chars for debugging

            # Now try to parse the JSON
            return json.loads(clean_content)

        except json.JSONDecodeError as e:
            print(f"    - Attempt {attempt + 1}: Failed to decode JSON from API response: {e}. Retrying...")
            if 'chat_response' in locals():
                print(f"    - Raw response preview: {chat_response.choices[0].message.content[:200]}...")
            time.sleep(5)
        except Exception as e:
            print(f"    - Attempt {attempt + 1}: An unexpected error occurred: {e}. Retrying...")
            time.sleep(5)

    print("    - Failed to generate data after multiple retries.")
    return None

def main():
    if not API_KEY:
        print("Error: MISTRAL_API_KEY environment variable not set.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python process_single_chunk_mistral.py \"<filename_of_chapter.txt>\"")
        print("Example: python process_single_chunk_mistral.py \"01_The Observation of Savage Peoples.txt\"")
        sys.exit(1)

    input_filename = sys.argv[1]
    filepath = os.path.join(INPUT_DIR, input_filename)

    if not os.path.exists(filepath):
        print(f"Error: The file '{input_filename}' was not found in the '{INPUT_DIR}' directory.")
        sys.exit(1)

    # Initialize the client using the new method as per migration guide
    client = Mistral(api_key=API_KEY)

    print(f"--- Processing: {input_filename} ---")

    with open(filepath, 'r', encoding='utf-8') as f_in:
        chapter_text = f_in.read()

    generated_data = generate_data_from_chunk(chapter_text, client)

    if generated_data and isinstance(generated_data, list):
        count = 0
        with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as f_out:
            for item in generated_data:
                if isinstance(item, dict) and all(
                        k in item for k in ["instruction", "spradley_type", "context", "output"]):
                    f_out.write(json.dumps(item, ensure_ascii=False) + '\n')
                    count += 1
                else:
                    print(f"    - Skipping malformed item: {item}")
        print(f"\nSuccessfully generated and appended {count} examples to '{OUTPUT_FILE_PATH}'.")
    else:
        print("\nFailed to generate valid data for this chapter. No data was written.")

if __name__ == "__main__":
    main()
