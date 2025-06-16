The Ethnographer's Digital Colleague
This repository contains the full code, data, and model artifacts for the research project, "The Ethnographer’s Digital Colleague: Prototyping a Reflexive AI Partner for Fieldwork Analysis," authored by Gürhan Camgöz.
This project details the creation of a fine-tuned Large Language Model (LLM) designed to act as a "digital colleague" for anthropologists and ethnographers. The model is trained to engage in methodologically aware dialogue, prompting researchers to think more deeply about their observations, analytical frameworks, and ethical considerations during the writing process.
For a full discussion of the project's theoretical background, methodology, and implications, please refer to the complete article. 
Repository Structure
This repository is organized to provide a clear and transparent view of the entire research pipeline, from source text processing to model fine-tuning.
/ │ ├── 📜 README.md             # This overview file │ ├── 📂 data/                  # The final, processed datasets │   ├── output_dataset.jsonl  # The full 511-example dataset │   ├── train.jsonl           # The 80% training split │   ├── validation.jsonl      # The 10% validation split │   └── test.jsonl            # The 10% held-out test split │ ├── 📂 model/                 # The fine-tuned model adapter │   └── ethno-colleague-final/  # LoRA adapter files ready for use │ ├── 📂 notebooks/ │   └── Ethno_Colleague_LLM.ipynb # The Jupyter Notebook for fine-tuning │ ├── 📂 scripts/               # Python scripts for the data pipeline │   ├── 01_split_thesis_subsections.py │   ├── 02_process_thesis_sections.py │   ├── 03_process_single_chunk_mistral.py │   ├── 04_process_personal_data.py │   ├── 05_split_dataset.py │   └── 06_analyze_dataset.py │ └── 📂 source_texts/          # The raw .txt files used for generation     ├── chapter_chunks/       # Chunks from the Anthropological Reader     └── thesis_subsections/   # Chunks from the author's Master's thesis 
Setup and Installation
The project was developed in a Python environment. To replicate the work, you will need the main dependencies, which can be installed via pip.
pip install -q transformers peft bitsandbytes accelerate datasets trl mistralai pypdf2 
A complete list of installations can be found in the Jupyter Notebook (/notebooks/Ethno_Colleague_LLM.ipynb).
You will also need a Mistral AI API key, set as an environment variable (MISTRAL_API_KEY), to run the data generation scripts.
How to Replicate the Project
The project can be replicated in two main stages: curating the dataset and fine-tuning the model.
1. The Data Curation Pipeline
The output_dataset.jsonl file was created by running the scripts in the /scripts/ directory in numerical order. This process involves:
	1	Splitting Source Texts: Scripts like 01_split_thesis_subsections.py ingest raw PDF files and segment them into thematically coherent .txt chunks, which are saved in the /source_texts/ subdirectories.
	2	Generating Data: Scripts 02 through 04 take these text chunks and use the Mistral Large API to generate the structured instruction/context/output examples. These are appended to a master file.
	3	Analyzing and Partitioning: The final scripts, 05_split_dataset.py and 06_analyze_dataset.py, shuffle the master dataset, analyze its contents, and split it into the final train.jsonl, validation.jsonl, and test.jsonl files found in the /data/ directory.
2. Fine-Tuning the Model
The model fine-tuning process is documented in the Jupyter Notebook:
/notebooks/Ethno_Colleague_LLM.ipynb
This notebook provides a step-by-step guide to:
	•	Loading the base mistralai/Mistral-7B-Instruct-v0.3 model.
	•	Configuring the QLoRA parameters for efficient training.
	•	Loading the train.jsonl and validation.jsonl datasets.
	•	Running the SFTTrainer to fine-tune the model.
	•	Saving the final model adapter, which is provided in the /model/ directory.
License
This project, including its code, data, and model artifacts, is released under the Apache 2.0 License. This permissive license was chosen for its compatibility with the license of the base model (mistralai/Mistral-7B-Instruct-v0.3) and to encourage the widest possible use, sharing, and adaptation within the academic and research communities.
Ethical Considerations and Data Privacy
This project was trained on a combination of canonical academic texts and the author's own personal academic writings, including a Master's thesis, field notes, and diaries.
A note on privacy: The source PDF files for personal diaries and raw, sensitive field notes are not included in this public repository. This is to protect the privacy of the author and the confidentiality of any research participants mentioned therein.
The shared dataset (output_dataset.jsonl) contains only the AI-generated training examples derived from these texts. While the contexts in the dataset are based on real experiences, they have been processed and reframed by the generator LLM, creating a layer of abstraction from the original source material. No raw, unpublished field notes are present in the dataset.
