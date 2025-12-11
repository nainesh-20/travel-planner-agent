import os
import sys
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

try:
    from crewai import LLM, Agent, Task, Crew
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

api_key = os.getenv("GOOGLE_API_KEY")
print(f"Checking API Key configuration...")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment or .env file")
else:
    print(f"API Key is set (Length: {len(api_key)})")
    if "your_google_api_key_here" in api_key:
        print("CRITICAL ERROR: API Key appears to be the PLACEHOLDER string!")
    elif len(api_key) < 30:
        print(f"WARNING: API Key seems too short ({len(api_key)} chars). Real keys are usually longer.")
        print(f"Value: {api_key}")
    else:
        print(f"API Key seems valid format (starts with: {api_key[:6]}...)")

print("\nTesting CrewAI / Gemini Connection...")
try:
    # Use the EXACT configuration from gemini2_travel_v2.py
    # Based on Step 98, it was "gemini/gemini-1.5-flash"
    model_name = "gemini/gemini-1.5-flash"
    print(f"Initializing LLM with model: {model_name}")
    
    llm = LLM(
        model=model_name,
        api_key=api_key
    )
    
    agent = Agent(
        role="Test Agent",
        goal="Verify API connection",
        backstory="I am a test agent.",
        llm=llm,
        verbose=True
    )
    
    task = Task(
        description="Reply with exactly three words: 'Connection is working'.",
        agent=agent,
        expected_output="A simple confirmation phrase."
    )
    
    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    
    print("Starting Crew execution...")
    result = crew.kickoff()
    print(f"\nSUCCESS! Result from AI: {result}")

except Exception as e:
    print(f"\nFAILURE! Error details:")
    print(str(e))
    # Print type of error
    print(f"Error Type: {type(e).__name__}")
