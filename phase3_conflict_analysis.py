"""
Phase 3: Detailed Conflict Analysis
Uses GPT-4 with few-shot learning to identify specific conflict types
Cost: ~$3-5 for 50 transcripts
"""

import pandas as pd
import json
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm
import config

# FEW-SHOT EXAMPLES - UPDATE THESE WITH YOUR REAL EXAMPLES
FEW_SHOT_EXAMPLES = """
EXAMPLE 1 (HAS CONFLICT - Pricing Dispute):
Customer: "You told me it would be $200 but now you're charging me $350? This doesn't make sense!"
Conflict Type: Pricing Dispute
Severity: 4/5
Trigger: Customer saw final bill different from quote

EXAMPLE 2 (HAS CONFLICT - Service Quality):
Customer: "I've been on hold for 30 minutes and transferred three times. Nobody seems to know what they're doing!"
Conflict Type: Service Quality Issue
Severity: 3/5
Trigger: Multiple transfers and long wait time

EXAMPLE 3 (HAS CONFLICT - Miscommunication):
Customer: "No, I specifically asked for the luxury suite and you booked the classic. I need this fixed now."
Conflict Type: Miscommunication
Severity: 3/5
Trigger: Booking error did not match request

EXAMPLE 4 (NO CONFLICT - Satisfied):
Customer: "Thank you so much for checking that. I'll call back after I discuss with my family."
No conflict present, customer is satisfied

EXAMPLE 5 (NO CONFLICT - Neutral Inquiry):
Customer: "Can you tell me what the total would be with all the fees included?"
No conflict present, just information seeking
"""

def analyze_conflict(client, transcript_text, file_name):
    """Detailed conflict analysis using GPT-4"""
    
    prompt = f"""You are analyzing customer service calls to identify conflicts and their characteristics.

CONFLICT TYPES TO IDENTIFY:
1. Pricing Dispute: Customer disagrees with costs/charges/billing
2. Service Quality Issue: Complaints about poor service, transfers, wait times
3. Miscommunication: Confusion, wrong information, booking errors
4. Unmet Expectations: Product/service didn't match what was promised
5. Other: Any other type of customer frustration

{FEW_SHOT_EXAMPLES}

NOW ANALYZE THIS TRANSCRIPT:
File: {file_name}

Transcript:
{transcript_text[:3500]}

Provide your analysis in valid JSON format:
{{
  "has_conflict": true or false,
  "conflict_types": ["type1", "type2"] or [],
  "severity": 1-5 (1=minor, 5=severe),
  "trigger_moment": "brief quote showing when conflict started or escalated",
  "customer_tone": "calm/frustrated/angry",
  "resolution_attempted": true or false,
  "resolution_successful": true or false or null,
  "key_phrases": ["phrase1", "phrase2"],
  "summary": "one sentence summary"
}}"""

    try:
        response = client.chat.completions.create(
            model=config.PHASE3_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "error": str(e),
            "has_conflict": None,
            "conflict_types": [],
            "severity": 0
        }

def main():
    print("=" * 80)
    print("PHASE 3: DETAILED CONFLICT ANALYSIS")
    print("=" * 80)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    # Load unsatisfied customers from Phase 1
    try:
        df = pd.read_csv(config.PHASE1_UNSATISFIED)
        print(f"\nLoaded {len(df)} unsatisfied customer transcripts from Phase 1")
    except FileNotFoundError:
        print("Error: phase1_unsatisfied_customers.csv not found. Run Phase 1 first.")
        return
    
    # Limit to top N by frustration level
    max_to_analyze = min(50, len(df))
    df_analyze = df.nlargest(max_to_analyze, 'frustration_level')
    print(f"Analyzing top {len(df_analyze)} most frustrated customers")
    
    # Analyze each transcript
    results = []
    for idx, row in tqdm(df_analyze.iterrows(), total=len(df_analyze), desc="Analyzing conflicts"):
        # Load full transcript
        file_found = False
        for data_dir in config.DATA_DIRS:
            file_path = Path(data_dir) / row['file']
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Analyze
                    analysis = analyze_conflict(client, data['text'], row['file'])
                    
                    # Combine with Phase 1 data
                                        # Extract transcript ID
                    transcript_id = row['file'].replace('_transcript.json', '')
                    
                    # Combine with Phase 1 data
                    result = {
                        'transcript_id': transcript_id,
                        'file': row['file'],
                        'directory': row['directory'],
                        'audio_duration_seconds': data.get('audio_duration', 0),
                        'asr_confidence': data.get('confidence', 0),
                        'phase1_sentiment': row['sentiment'],
                        'phase1_frustration': row['frustration_level'],
                        'has_conflict': analysis.get('has_conflict'),
                        'conflict_types': ', '.join(analysis.get('conflict_types', [])),
                        'severity': analysis.get('severity'),
                        'trigger_moment': analysis.get('trigger_moment', ''),
                        'customer_tone': analysis.get('customer_tone', ''),
                        'resolution_attempted': analysis.get('resolution_attempted'),
                        'resolution_successful': analysis.get('resolution_successful'),
                        'key_phrases': ', '.join(analysis.get('key_phrases', [])),
                        'summary': analysis.get('summary', ''),
                        'full_text': data['text'],  # ← ADD FULL TEXT
                        'error': analysis.get('error', '')
                    }
                    results.append(result)
                    file_found = True
                    break
                    
                except Exception as e:
                    print(f"\nError processing {row['file']}: {e}")
        
        if not file_found:
            print(f"\nWarning: Could not find file {row['file']}")
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(config.PHASE3_OUTPUT, index=False)
    
    # Print statistics
    print("\n" + "=" * 80)
    print("CONFLICT ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Total transcripts analyzed: {len(results_df)}")
    
    conflict_df = results_df[results_df['has_conflict'] == True]
    print(f"\nTranscripts with conflicts: {len(conflict_df)} ({len(conflict_df)/len(results_df)*100:.1f}%)")
    
    if len(conflict_df) > 0:
        print("\nConflict types breakdown:")
        all_types = []
        for types in conflict_df['conflict_types'].dropna():
            if types:
                all_types.extend([t.strip() for t in types.split(',')])
        
        from collections import Counter
        type_counts = Counter(all_types)
        for conflict_type, count in type_counts.most_common():
            print(f"  {conflict_type}: {count}")
        
        print("\nSeverity distribution:")
        print(conflict_df['severity'].value_counts().sort_index())
    
    print(f"\n✅ Results saved to: {config.PHASE3_OUTPUT}")
    
    # Cost estimate
    avg_tokens_per_call = 1500
    cost_per_1k_tokens = 0.01  # GPT-4 input
    estimated_cost = (len(results_df) * avg_tokens_per_call / 1000) * cost_per_1k_tokens
    print(f"\nEstimated cost: ${estimated_cost:.2f}")

if __name__ == "__main__":
    main()