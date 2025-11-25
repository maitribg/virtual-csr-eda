"""
Simple runner - executes all 3 steps in order.
"""

import subprocess

print("="*60)
print("CSR TRAINING PROMPT GENERATOR")
print("="*60)

print("\n[1/3] Generating customer profiles...")
subprocess.run(["python", "profile_generator.py"])

print("\n[2/3] Creating training scenarios...")
subprocess.run(["python", "scenario_generator.py"])

print("\n[3/3] Exporting prompts for Playground...")
subprocess.run(["python", "prompt_exporter.py"])

print("\n" + "="*60)
print("✅ COMPLETE! Check the prompt_*.json files")
print("="*60)