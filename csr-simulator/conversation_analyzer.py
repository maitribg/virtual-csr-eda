import sys
sys.path.append('..')  # Access parent config
import config

import json
import os
from openai import OpenAI

# Setup
client = OpenAI(api_key=config.OPENAI_API_KEY)

def load_conversation(chat_file):
    """Load the exported chat history"""
    with open(chat_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_scenario(scenario_file, persona_type):
    """Load the specific scenario for this customer type"""
    with open(scenario_file, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    # Find the matching scenario
    for scenario in scenarios:
        if scenario.get('persona_type', '').lower() == persona_type.lower():
            return scenario
    
    # If not found, return first one as fallback
    print(f"⚠️  Warning: No scenario found for '{persona_type}', using first available")
    return scenarios[0] if scenarios else {}

def extract_dialogue(conversation):
    """Extract clean user/assistant exchanges"""
    dialogue = []
    # Get the last conversation entry (most recent)
    last_convo = conversation[-1]
    
    for msg in last_convo['messages']:
        role = msg['role']
        if role in ['user', 'assistant']:
            content = msg['content'][0]['text'] if msg['content'] else ''
            if content.strip():  # Skip empty messages
                dialogue.append({
                    'role': 'Customer (AI)' if role == 'assistant' else 'CSR (You)',
                    'message': content
                })
    return dialogue

def analyze_performance(dialogue, scenario):
    """Use GPT-4 to analyze CSR performance"""
    
    # Format dialogue for analysis
    dialogue_text = "\n\n".join([
        f"{turn['role']}: {turn['message']}" 
        for turn in dialogue
    ])
    
    # Extract ideal responses
    ideal_behaviors = []
    for turn in scenario.get('conversation_turns', []):
        ideal_behaviors.append(f"- {turn.get('ideal_csr_response', 'N/A')}")
    
    prompt = f"""You are an expert customer service trainer. Analyze this conversation between a CSR trainee and a difficult customer.

TRAINING SCENARIO CONTEXT:
- Customer Type: {scenario.get('persona_type', 'N/A')}
- Customer Problem: {scenario.get('scenario_description', 'N/A')}
- Success Criteria: {', '.join(scenario.get('success_criteria', []))}

IDEAL CSR BEHAVIORS:
{chr(10).join(ideal_behaviors)}

ACTUAL CONVERSATION:
{dialogue_text}

PROVIDE DETAILED ANALYSIS:

1. **Overall Performance Score (1-10):**
   - Provide a score and brief justification

2. **What the CSR Did WELL:**
   - List 3-5 specific positive actions with examples from the conversation

3. **Critical MISTAKES:**
   - List 3-5 specific errors or missed opportunities with examples

4. **Conflict Escalation Analysis:**
   - Did the CSR escalate or de-escalate the situation?
   - Identify the turning points in the conversation

5. **Comparison to Ideal Responses:**
   - How did actual responses compare to training scenario expectations?
   - What techniques from the ideal responses were missing?

6. **Key Learning Moments:**
   - Identify 3-5 teachable moments from this conversation

7. **Actionable Recommendations:**
   - Provide 5-7 specific, practical improvements for next time

8. **Did the CSR Meet Success Criteria?**
   - Evaluate against each criterion from the training scenario

Format the response as clear, structured feedback suitable for CSR training.
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def generate_report(chat_file, scenario_file, persona_type, output_file):
    """Generate full analysis report"""
    
    print(f"\n{'='*60}")
    print("CSR CONVERSATION ANALYZER")
    print('='*60)
    print(f"📁 Chat file: {chat_file}")
    print(f"📁 Scenario file: {scenario_file}")
    print(f"👤 Customer type: {persona_type}")
    print('='*60 + "\n")
    
    print("Loading conversation...")
    conversation = load_conversation(chat_file)
    
    print("Loading training scenario...")
    scenario = load_scenario(scenario_file, persona_type)
    
    print("Extracting dialogue...")
    dialogue = extract_dialogue(conversation)
    print(f"  → Found {len(dialogue)} conversation turns")
    
    print("\n🤖 Analyzing performance with GPT-4...")
    print("   (This may take 30-60 seconds...)")
    analysis = analyze_performance(dialogue, scenario)
    
    # Create report
    report = {
        "chat_file": chat_file,
        "scenario_file": scenario_file,
        "customer_type": scenario.get('persona_type', 'Unknown'),
        "total_turns": len(dialogue),
        "analysis": analysis,
        "full_dialogue": dialogue
    }
    
    # Save JSON report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Save readable text version
    text_output = output_file.replace('.json', '.txt')
    with open(text_output, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("CSR PERFORMANCE ANALYSIS REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Customer Type: {report['customer_type']}\n")
        f.write(f"Total Conversation Turns: {report['total_turns']}\n")
        f.write(f"Chat File: {chat_file}\n\n")
        f.write("="*60 + "\n")
        f.write("DETAILED ANALYSIS\n")
        f.write("="*60 + "\n\n")
        f.write(analysis)
        f.write("\n\n" + "="*60 + "\n")
        f.write("FULL CONVERSATION TRANSCRIPT\n")
        f.write("="*60 + "\n\n")
        for turn in dialogue:
            f.write(f"{turn['role']}:\n{turn['message']}\n\n")
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 JSON report: {output_file}")
    print(f"📄 Text report: {text_output}")
    print(f"\n" + "="*60)
    print("ANALYSIS PREVIEW:")
    print("="*60)
    print(analysis[:500] + "...\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("\n" + "="*60)
        print("USAGE:")
        print("="*60)
        print("python conversation_analyzer.py <chat.json> <persona_type> <scenario.json>\n")
        print("EXAMPLES:")
        print("-" * 60)
        print("python conversation_analyzer.py angry_customer_chat.json angry training_scenarios.json")
        print("python conversation_analyzer.py confused_chat.json confused training_scenarios.json")
        print("python conversation_analyzer.py unsatisfied_chat.json unsatisfied training_scenarios.json")
        print("\n" + "="*60 + "\n")
        sys.exit(1)
    
    chat_file = sys.argv[1]
    persona_type = sys.argv[2]
    scenario_file = sys.argv[3]
    
    # Generate output filename
    output_file = f"analysis_{persona_type}_{os.path.basename(chat_file)}"
    
    generate_report(chat_file, scenario_file, persona_type, output_file)
    
    print("\n💡 Review the analysis files for detailed feedback!")
    print("="*60 + "\n")