import json
import random
import os

# --- Configuration ---

# The single, large dataset file you've created.
INPUT_FILE = "output_dataset.jsonl"

# The names for your output files.
TRAIN_FILE = "train.jsonl"
VALIDATION_FILE = "validation.jsonl"
TEST_FILE = "test.jsonl"

# Define the split ratios. They should sum to 1.0.
# A standard 80/10/10 split is a great choice.
SPLIT_RATIOS = {
    "train": 0.8,
    "validation": 0.1,
    "test": 0.1
}


# --- Main Script ---

def split_dataset():
    """
    Reads the main dataset, shuffles it, and splits it into
    training, validation, and test sets according to the defined ratios.
    """
    print(f"--- Starting Dataset Split ---")

    # 1. Read all lines from the input file
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        print(f"Successfully read {len(all_lines)} total examples from '{INPUT_FILE}'.")
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found. Please make sure it's in the same directory.")
        return

    if not all_lines:
        print("Error: Input file is empty.")
        return

    # 2. Shuffle the data
    # This is crucial to ensure that your splits are random and not biased
    # by the order in which data was generated (e.g., all data from one chapter
    # ending up in the same split).
    random.shuffle(all_lines)
    print("Randomly shuffled all examples.")

    # 3. Calculate split indices
    total_examples = len(all_lines)
    train_end_index = int(total_examples * SPLIT_RATIOS["train"])
    validation_end_index = train_end_index + int(total_examples * SPLIT_RATIOS["validation"])

    # The test set will be whatever is left over, ensuring all data is used.

    # 4. Create the splits
    train_lines = all_lines[:train_end_index]
    validation_lines = all_lines[train_end_index:validation_end_index]
    test_lines = all_lines[validation_end_index:]

    # 5. Write the splits to their respective files
    def write_to_file(filename, lines):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(line)
            print(f"Successfully wrote {len(lines)} examples to '{filename}'.")
        except IOError as e:
            print(f"Error writing to file '{filename}': {e}")

    write_to_file(TRAIN_FILE, train_lines)
    write_to_file(VALIDATION_FILE, validation_lines)
    write_to_file(TEST_FILE, test_lines)

    print("\n--- Dataset splitting complete! ---")
    print("You are now ready to upload 'train.jsonl' and 'validation.jsonl' to Colab.")


if __name__ == "__main__":
    split_dataset()

