#!/usr/bin/env python3
"""
Quick CLI examples for prompt-based recording using the gemini-workflow command.
"""

import subprocess
import sys
import os

def check_api_key():
    """Check if API key is configured."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ GEMINI_API_KEY not configured!")
        print("\n📋 Setup Instructions:")
        print("1. Get API key: https://makersuite.google.com/app/apikey")
        print("2. Edit .env file and set: GEMINI_API_KEY=your_actual_key")
        return False
    return True

def run_cli_examples():
    """Show CLI examples for prompt-based recording."""
    
    print("🤖 Gemini Workflow Automation - CLI Examples")
    print("=" * 60)
    
    if not check_api_key():
        print("\n⚠️  Set up API key first, then run these commands:")
    else:
        print("✅ API key configured - you can run these examples:")
    
    print("\n🎯 CLI Recording Examples:")
    print("=" * 40)
    
    examples = [
        {
            "name": "GitHub Search",
            "command": 'gemini-workflow record "Go to GitHub, search for playwright, and click the first result" --name github_search --initial-url https://github.com'
        },
        {
            "name": "Wikipedia Search", 
            "command": 'gemini-workflow record "Search for artificial intelligence and read the first paragraph" --name wiki_ai --initial-url https://wikipedia.org'
        },
        {
            "name": "Google Search",
            "command": 'gemini-workflow record "Search for python automation tutorials" --name google_python --initial-url https://google.com'
        },
        {
            "name": "Weather Check",
            "command": 'gemini-workflow record "Check weather for San Francisco" --name weather_sf --initial-url https://weather.com'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}:")
        print(f"   {example['command']}")
    
    print("\n🎮 After Recording - Replay Examples:")
    print("=" * 40)
    print("# List all workflows")
    print("gemini-workflow list")
    print()
    print("# Execute a workflow")
    print("gemini-workflow execute workflows/definitions/github_search.json")
    print()
    print("# Get workflow info")
    print("gemini-workflow info workflows/definitions/github_search.json")
    
    print("\n🔄 Parameterized Workflows:")
    print("=" * 30)
    print("# Record with variables")
    print('gemini-workflow record "Search for {search_term} on Google" --name google_search_template')
    print()
    print("# Execute with variables")
    print('gemini-workflow execute google_search_template.json --var search_term="machine learning"')
    
    if check_api_key():
        print("\n🚀 Ready to try? Here's a simple starter:")
        print("=" * 45)
        print('gemini-workflow record "Go to example.com and click Learn more" --name simple_test --initial-url https://example.com')
        
        run_now = input("\n▶️  Run the simple example now? (y/N): ").strip().lower()
        if run_now in ['y', 'yes']:
            cmd = [
                'gemini-workflow', 'record', 
                'Go to example.com and click Learn more',
                '--name', 'simple_test',
                '--initial-url', 'https://example.com',
                '--verbose'
            ]
            
            print(f"\n🏃 Running: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, check=True, capture_output=False)
                print("\n✅ Recording completed!")
                
                test_now = input("\n🎮 Test the recorded workflow? (y/N): ").strip().lower()
                if test_now in ['y', 'yes']:
                    test_cmd = ['gemini-workflow', 'execute', 'workflows/definitions/simple_test.json']
                    print(f"\n🏃 Running: {' '.join(test_cmd)}")
                    subprocess.run(test_cmd, check=True, capture_output=False)
                    
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Command failed: {e}")
            except FileNotFoundError:
                print("\n❌ gemini-workflow command not found. Make sure virtual environment is activated.")

if __name__ == "__main__":
    run_cli_examples()