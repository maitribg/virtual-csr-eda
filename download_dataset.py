from datasets import load_dataset

# Load dataset directly without triggering pandas conversion
dataset = load_dataset("AIxBlock/92k-real-world-call-center-scripts-english")

# Just save the HuggingFace Dataset object
dataset.save_to_disk("data/call_center_dataset")
