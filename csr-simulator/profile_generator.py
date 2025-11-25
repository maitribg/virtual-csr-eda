"""
Step 1: Generate customer profiles from real conflict data.
Simple script - just loads conflicts and creates personas.
"""

import sys
sys.path.append('..')  # Access parent config
import config

import pandas as pd
import json
from openai import OpenAI

# Setup
client = OpenAI(api_key=config.OPENAI_API_KEY)
conflict_data = pd.read_csv('../phase3_conflict_analysis.csv')

def create_customer_profile(persona_type, severity_level=3):
    """
    Generate ONE customer profile based on real conflict.
    
    persona_type: 'angry', 'confused', or 'demanding'
    severity_level: How bad the conflict is (3-5)
    """
    
    # Find a real conflict that matches
    matching_conflicts = conflict_data[conflict_data['severity'] >= severity_level]
    real_conflict = matching_conflicts.sample(1).iloc[0]
    
    # Ask GPT to create a realistic customer profile
    prompt = f"""Based on this REAL customer conflict from our data, create a detailed customer profile:

Real Conflict Details:
- Type: {real_conflict['conflict_types']}
- Severity: {real_conflict['severity']}/5
- What triggered it: {real_conflict['trigger_moment']}
- Customer's tone: {real_conflict['customer_tone']}

Create a {persona_type.upper()} customer profile as JSON:
{{
  "name": "realistic first and last name",
  "age": number,
  "background": "brief background (job, family situation)",
  "current_problem": "what went wrong (based on real conflict above)",
  "emotional_state": "how they feel right now",
  "frustration_level": {real_conflict['severity']},
  "what_they_want": "what would make them happy",
  "communication_style": "how they talk when upset",
  "escalation_triggers": ["what makes them MORE angry"],
  "de_escalation_cues": ["what calms them down"],
  "hidden_concern": "deeper worry they might not say directly"
}}"""
    
    # Call GPT
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    
    # Parse and add metadata
    profile = json.loads(response.choices[0].message.content)
    profile['persona_type'] = persona_type
    profile['source_conflict_id'] = real_conflict['transcript_id']
    
    return profile


# Generate profiles - 3 total
if __name__ == "__main__":
    print("Generating customer profiles...\n")
    
    all_profiles = []
    
    # Create 1 angry customer
    print(f"Creating angry customer...")
    profile = create_customer_profile('angry', severity_level=4)
    all_profiles.append(profile)
    
    # Create 1 unsatisfied customer
    print(f"Creating unsatisfied customer...")
    profile = create_customer_profile('unsatisfied', severity_level=3)
    all_profiles.append(profile)
    
    # Create 1 confused customer
    print(f"Creating confused customer...")
    profile = create_customer_profile('confused', severity_level=3)
    all_profiles.append(profile)
    
    # Save all profiles
    with open('customer_profiles.json', 'w') as f:
        json.dump(all_profiles, f, indent=2)
    
    print(f"\n✅ Generated {len(all_profiles)} customer profiles")
    print("Saved to: customer_profiles.json")