import os
import agentstats
from openai import OpenAI

# Start watching SDKs
agentstats.watch()

client = OpenAI(api_key="fake-key-to-trigger-error")

def run_agent():
    print("Agent is making a request...")
    try:
        # This will fail because the API key is fake
        client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    except Exception as e:
        print(f"Agent caught exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    run_agent()
    print("\n--- AgentStats Report ---")
    agentstats.report()
