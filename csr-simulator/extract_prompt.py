"""
Simple script to extract clean, readable prompt from JSON.
"""

import json
import sys

def extract_clean_prompt(json_file):
    """Extract and print the system prompt in readable format."""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get the system prompt
    prompt = data['system_prompt']
    
    # Print it cleanly
    print(prompt)
    print("\n" + "="*60)
    print("Copy the text above ↑ and paste into OpenAI Playground")
    print("="*60)
    
    # Optionally save to a .txt file
    output_file = json_file.replace('.json', '_clean.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"\nAlso saved to: {output_file}")

# Usage
if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_clean_prompt(sys.argv[1])
    else:
        # Default: extract all prompts
        import glob
        for json_file in glob.glob('prompt_*.json'):
            print(f"\nExtracting from {json_file}...")
            extract_clean_prompt(json_file)