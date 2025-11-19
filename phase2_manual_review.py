"""
Phase 2: Manual Review Helper
Helps you review unsatisfied customers and select examples for few-shot learning
"""

import pandas as pd
import json
from pathlib import Path

def display_transcript(file_path):
    """Display full transcript for review"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("\n" + "=" * 80)
            print(f"File: {file_path.name}")
            print("=" * 80)
            print(data['text'])
            print("\n" + "-" * 80)
            print(f"Confidence: {data.get('confidence', 'N/A')}")
            print(f"Duration: {data.get('audio_duration', 'N/A')} seconds")
            print("=" * 80)
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    print("=" * 80)
    print("PHASE 2: MANUAL REVIEW HELPER")
    print("=" * 80)
    
    # Load unsatisfied customers
    try:
        df = pd.read_csv('phase1_unsatisfied_customers.csv')
        print(f"\nLoaded {len(df)} unsatisfied customer transcripts")
    except FileNotFoundError:
        print("Error: phase1_unsatisfied_customers.csv not found. Run phase1 first.")
        return
    
    print("\nTop 10 most frustrated customers:")
    print(df.nlargest(10, 'frustration_level')[['file', 'sentiment', 'frustration_level', 'reason']])
    
    print("\n" + "=" * 80)
    print("INTERACTIVE REVIEW")
    print("=" * 80)
    print("Type a row number to view full transcript, or 'q' to quit")
    
    while True:
        choice = input("\nEnter row number (0-{}): ".format(len(df)-1))
        
        if choice.lower() == 'q':
            break
            
        try:
            idx = int(choice)
            if 0 <= idx < len(df):
                row = df.iloc[idx]
                
                # Find the file
                for data_dir in ['data/medicare_inbound/medicare_inbound', 
                                'data/PII_Redacted_Transcripts_aixblock-automotive-stereo-inbound-104h']:
                    file_path = Path(data_dir) / row['file']
                    if file_path.exists():
                        display_transcript(file_path)
                        
                        # Ask for classification
                        print("\nClassify this transcript:")
                        print("1. Pricing Dispute")
                        print("2. Service Quality Issue")
                        print("3. Wait Time Frustration")
                        print("4. Miscommunication")
                        print("5. Unmet Expectations")
                        print("6. No real conflict (false positive)")
                        print("0. Skip")
                        
                        classification = input("Enter number: ")
                        if classification != '0':
                            # You can save these classifications
                            print(f"Classified as: {classification}")
                        break
            else:
                print("Invalid row number")
        except ValueError:
            print("Invalid input")

if __name__ == "__main__":
    main()