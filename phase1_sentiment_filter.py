"""
Phase 1: Sentiment Analysis and Filtering
Uses GPT-3.5-turbo to identify unsatisfied customers
Cost: ~$0.50-1.00 for 100 transcripts
"""

import json
import random
from pathlib import Path
from openai import OpenAI
import pandas as pd
from tqdm import tqdm
import config


random.seed(2002)
def load_random_sample(data_dirs, sample_size):
    """Load random sample of transcripts from all data directories"""
    print(f"Loading transcripts from {len(data_dirs)} directories...")
    all_files = []
    
    for dir_path in data_dirs:
        json_files = list(Path(dir_path).glob("*.json"))
        print(f"  Found {len(json_files)} files in {dir_path}")
        all_files.extend(json_files)
    
    print(f"\nTotal files available: {len(all_files)}")
    sample_size = min(sample_size, len(all_files))
    sampled = random.sample(all_files, sample_size)
    
    transcripts = []
    for file in tqdm(sampled, desc="Loading files"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                transcripts.append({
                    'file': file.name,
                    'directory': file.parent.name,
                    'text': data['text'],
                    'confidence': data.get('confidence', 0),
                    'duration': data.get('audio_duration', 0)
                })
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    return transcripts

def analyze_sentiment(client, transcript_text):
    """Analyze sentiment using GPT-3.5-turbo"""
    # Truncate to save costs
    truncated_text = transcript_text[:config.MAX_TRANSCRIPT_LENGTH]
    
    prompt = f"""Analyze this customer service call transcript and classify the customer's sentiment.

Transcript: {truncated_text}

Provide:
1. Overall sentiment: SATISFIED, NEUTRAL, UNSATISFIED, or ANGRY
2. Frustration level (1-5): 1=calm, 5=extremely frustrated
3. Brief reason (one sentence)

Format your response as: SENTIMENT|FRUSTRATION_SCORE|REASON
Example: UNSATISFIED|4|Customer repeatedly expressed frustration about billing errors"""

    try:
        response = client.chat.completions.create(
            model=config.PHASE1_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR|0|{str(e)}"

def main():
    print("=" * 80)
    print("PHASE 1: SENTIMENT FILTERING")
    print("=" * 80)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    # Load transcripts
    transcripts = load_random_sample(config.DATA_DIRS, config.PHASE1_SAMPLE_SIZE)
    print(f"\nLoaded {len(transcripts)} transcripts")
    
    # Analyze sentiment
    print(f"\nAnalyzing sentiment using {config.PHASE1_MODEL}...")
    results = []
    
    for i, trans in enumerate(tqdm(transcripts, desc="Processing")):
        sentiment_result = analyze_sentiment(client, trans['text'])
        
        # Parse result
        parts = sentiment_result.split('|')
        sentiment = parts[0] if len(parts) > 0 else "UNKNOWN"
        frustration = parts[1] if len(parts) > 1 else "0"
        reason = parts[2] if len(parts) > 2 else ""
        
                # Extract transcript ID from filename (remove _transcript.json)
        transcript_id = trans['file'].replace('_transcript.json', '')
        
        results.append({
            'transcript_id': transcript_id,
            'file': trans['file'],
            'directory': trans['directory'],
            'sentiment': sentiment,
            'frustration_level': frustration,
            'reason': reason,
            'audio_duration_seconds': trans['duration'],
            'asr_confidence': trans['confidence'],
            'full_text': trans['text']  # ← FULL TEXT, not preview
        })
        
        # Save checkpoint every 25
        if (i + 1) % 25 == 0:
            checkpoint_df = pd.DataFrame(results)
            checkpoint_df.to_csv(f'checkpoint_{i+1}.csv', index=False)
            print(f"\nCheckpoint saved at {i+1} transcripts")
    
    # Save all results
    df = pd.DataFrame(results)
    df.to_csv(config.PHASE1_OUTPUT, index=False)
    print(f"\n✅ All results saved to: {config.PHASE1_OUTPUT}")
    
    # Filter unsatisfied customers
    unsatisfied_mask = df['sentiment'].str.contains('UNSATISFIED|ANGRY', case=False, na=False)
    unsatisfied = df[unsatisfied_mask]
    unsatisfied.to_csv(config.PHASE1_UNSATISFIED, index=False)
    
    # Print statistics
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total transcripts analyzed: {len(df)}")
    print(f"\nSentiment breakdown:")
    print(df['sentiment'].value_counts())
    print(f"\nUnsatisfied/Angry customers: {len(unsatisfied)} ({len(unsatisfied)/len(df)*100:.1f}%)")
    print(f"Saved to: {config.PHASE1_UNSATISFIED}")
    
    # Cost estimate
    avg_tokens_per_call = 700  # Rough estimate
    cost_per_1k_tokens = 0.0015  # GPT-3.5-turbo input + output
    estimated_cost = (len(df) * avg_tokens_per_call / 1000) * cost_per_1k_tokens
    print(f"\nEstimated cost: ${estimated_cost:.2f}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("1. Review phase1_unsatisfied_customers.csv")
    print("2. Manually identify 5-10 real conflict examples")
    print("3. Run phase3_conflict_analysis.py with your examples")
    print("=" * 80)

if __name__ == "__main__":
    main()