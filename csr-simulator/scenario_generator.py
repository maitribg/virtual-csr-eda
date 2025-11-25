"""
Step 2: Create conversation scenarios with ideal responses.
Takes profiles and creates training scenarios.
"""

import sys
sys.path.append('..')
import config

import json
from openai import OpenAI

# Setup
client = OpenAI(api_key=config.OPENAI_API_KEY)

def create_scenario(profile):
    """
    Create a conversation scenario with ground truth responses.
    
    Input: customer profile (from step 1)
    Output: scenario with ideal CSR responses
    """
    
    # Detailed prompt for creating scenarios
    prompt = f"""You are designing a CSR training scenario based on this customer profile:

{json.dumps(profile, indent=2)}

Create a realistic conversation scenario with these components:

1. OPENING: What does the customer say to start the call?
2. CONVERSATION FLOW: 4-5 realistic back-and-forth exchanges
3. IDEAL CSR RESPONSES: What should a good CSR say at each turn?
4. SUCCESS METRICS: How do we know if CSR handled it well?

Return as JSON:
{{
  "scenario_id": "unique_id",
  "opening_statement": "customer's first words",
  "conversation_turns": [
    {{
      "turn_number": 1,
      "likely_customer_response": "what customer might say",
      "ideal_csr_response": "best way for CSR to respond",
      "why_this_works": "explanation of the strategy",
      "common_mistakes": ["things CSRs often do wrong here"]
    }}
  ],
  "success_criteria": ["measurable goals like 'customer tone improves'"],
  "learning_objectives": ["skills this scenario teaches"],
  "estimated_difficulty": "easy/medium/hard"
}}

Make it realistic - base it on the actual conflict patterns!"""
    
    # Call GPT
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.6
    )
    
    scenario = json.loads(response.choices[0].message.content)
    scenario['profile_id'] = profile.get('name', 'unknown')
    scenario['persona_type'] = profile['persona_type']
    
    return scenario


# Generate scenarios for all profiles
if __name__ == "__main__":
    print("Generating training scenarios...\n")
    
    # Load profiles from step 1
    with open('customer_profiles.json', 'r') as f:
        profiles = json.load(f)
    
    scenarios = []
    
    for i, profile in enumerate(profiles, 1):
        print(f"Creating scenario {i}/{len(profiles)} for {profile['name']}...")
        scenario = create_scenario(profile)
        scenarios.append(scenario)
    
    # Save scenarios
    with open('training_scenarios.json', 'w') as f:
        json.dump(scenarios, f, indent=2)
    
    print(f"\nGenerated {len(scenarios)} training scenarios")
    print("Saved to: training_scenarios.json")