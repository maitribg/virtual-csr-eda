"""
Step 3: Export prompts ready for OpenAI Playground.
Creates JSON files you can copy-paste into Playground.
"""

import json

def create_playground_prompt(profile, scenario):
    """
    Create a system prompt for OpenAI Playground.
    This is the detailed prompt that makes the AI act like the customer.
    """
    
    system_prompt = f"""You are roleplaying as {profile['name']}, a real customer calling customer service.

═══════════════════════════════════════════════════════
YOUR PROFILE
═══════════════════════════════════════════════════════
Age: {profile['age']}
Background: {profile['background']}
Emotional State: {profile['emotional_state']} (Frustration: {profile['frustration_level']}/5)

═══════════════════════════════════════════════════════
YOUR PROBLEM
═══════════════════════════════════════════════════════
{profile['current_problem']}

What you want: {profile['what_they_want']}
Hidden concern: {profile['hidden_concern']}

═══════════════════════════════════════════════════════
HOW YOU BEHAVE
═══════════════════════════════════════════════════════
Communication style: {profile['communication_style']}

You get MORE upset if the CSR:
{chr(10).join('- ' + trigger for trigger in profile['escalation_triggers'])}

You calm down if the CSR:
{chr(10).join('- ' + cue for cue in profile['de_escalation_cues'])}

═══════════════════════════════════════════════════════
CONVERSATION RULES
═══════════════════════════════════════════════════════
1. Start with: "{scenario['opening_statement']}"
2. Stay in character - you are NOT a helpful AI assistant
3. React naturally to what the CSR says
4. Keep responses short and realistic (2-4 sentences)
5. Show emotion through your words
6. Don't make it easy - be a real customer!

BEGIN THE CONVERSATION NOW."""
    
    return system_prompt


def export_for_playground(profile, scenario, output_filename):
    """
    Create a complete JSON file ready for OpenAI Playground.
    """
    
    system_prompt = create_playground_prompt(profile, scenario)
    
    export_data = {
        # What you paste into Playground
        "system_prompt": system_prompt,
        
        # Settings for Playground
        "model_settings": {
            "model": "gpt-4-turbo",
            "temperature": 0.7,
            "max_tokens": 500
        },
        
        # How to use this
        "instructions": [
            "1. Copy the 'system_prompt' text above",
            "2. Open OpenAI Playground (platform.openai.com/playground)",
            "3. Paste into 'System' message box",
            "4. Set temperature to 0.7",
            "5. Start the conversation - customer will begin automatically",
            "6. After training, export the chat log"
        ],
        
        # Success metrics for this scenario
        "success_criteria": scenario['success_criteria'],
        "learning_objectives": scenario['learning_objectives'],
        
        # Ground truth answers (for later analysis)
        "ideal_responses": scenario['conversation_turns']
    }
    
    # Save to file
    with open(output_filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return export_data


# Export all profiles and scenarios
if __name__ == "__main__":
    print("Exporting prompts for OpenAI Playground...\n")
    
    # Load data from previous steps
    with open('customer_profiles.json', 'r') as f:
        profiles = json.load(f)
    
    with open('training_scenarios.json', 'r') as f:
        scenarios = json.load(f)
    
    # Export each one
    for i, (profile, scenario) in enumerate(zip(profiles, scenarios), 1):
        persona = profile['persona_type']
        filename = f"prompt_{persona}_{i}.json"
        
        export_for_playground(profile, scenario, filename)
        print(f"✅ Exported: {filename}")
    
    print(f"\n🎯 Generated {len(profiles)} prompt files")
    print("\nTo use: Open any prompt file, copy 'system_prompt', paste into Playground")