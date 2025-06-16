import json
from collections import Counter
import re

# --- Configuration ---
# Set this to the path of your generated dataset file.
DATASET_FILE = "output_dataset.jsonl"


def analyze_dataset(file_path):
    """
    Reads a .jsonl file and performs a detailed analysis of its content.
    """
    total_examples = 0
    spradley_types = []
    instruction_word_counts = []
    context_word_counts = []
    output_word_counts = []

    all_instructions = []
    all_outputs = []

    print(f"--- Analyzing Dataset: {file_path} ---")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Load each line as a JSON object
                    data = json.loads(line.strip())

                    # --- Basic Counts ---
                    total_examples += 1
                    spradley_types.append(data.get("spradley_type", "N/A"))

                    # --- Text Analysis ---
                    instruction = data.get("instruction", "")
                    context = data.get("context", "")
                    output = data.get("output", "")

                    instruction_word_counts.append(len(instruction.split()))
                    context_word_counts.append(len(context.split()))
                    output_word_counts.append(len(output.split()))

                    all_instructions.append(instruction)
                    all_outputs.append(output)

                except json.JSONDecodeError:
                    print(f"Warning: Skipping a malformed line: {line.strip()}")
                except KeyError as e:
                    print(f"Warning: Skipping line due to missing key: {e} in {line.strip()}")

    except FileNotFoundError:
        print(f"\nError: The file '{file_path}' was not found.")
        print("Please make sure your generated dataset file has the correct name and is in the same directory.")
        return

    if total_examples == 0:
        print("No valid examples found in the file.")
        return

    # --- Print Report ---
    print("\n--- DATASET OVERVIEW ---")
    print(f"Total Number of Examples: {total_examples}")

    # 1. Distribution of Spradley Types
    print("\n1. Distribution of Spradley Question Types:")
    spradley_counts = Counter(spradley_types)
    for s_type, count in spradley_counts.items():
        percentage = (count / total_examples) * 100
        print(f"  - {s_type}: {count} examples ({percentage:.1f}%)")

    # 2. Length Analysis
    print("\n2. Analysis of Text Length (in words):")

    def print_stats(name, counts):
        if not counts: return
        avg = sum(counts) / len(counts)
        print(f"  - {name}:")
        print(f"    - Average Length: {avg:.1f} words")
        print(f"    - Min Length:     {min(counts)} words")
        print(f"    - Max Length:     {max(counts)} words")

    print_stats("Instruction", instruction_word_counts)
    print_stats("Context", context_word_counts)
    print_stats("Output (Question)", output_word_counts)

    # 3. Common Instruction Keywords
    print("\n3. Most Common Keywords in Instructions:")
    instruction_text = " ".join(all_instructions)
    # Simple regex to find words, ignoring case
    instruction_words = re.findall(r'\b\w+\b', instruction_text.lower())
    instruction_word_counts = Counter(instruction_words)
    # Ignore common "stop words" for a more meaningful analysis
    stop_words = {'a', 'an', 'the', 'ask', 'to', 'of', 'in', 'is', 'for', 'based', 'on', 'and', 'that', 'with'}
    for word in stop_words:
        del instruction_word_counts[word]
    print(f"  {instruction_word_counts.most_common(10)}")

    print("\n--- ANALYSIS COMPLETE ---")


def main():
    """Main function to run the analysis."""
    analyze_dataset(DATASET_FILE)


if __name__ == "__main__":
    main()
