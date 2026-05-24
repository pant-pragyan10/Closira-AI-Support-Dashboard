import os
import json
from dotenv import load_dotenv

from utils.groq_client import GroqClient


def clean_key(k: str) -> str:
    if not k:
        return ""
    return k.strip().strip('"').strip("'")


def main():
    load_dotenv()
    raw = os.getenv("GROQ_API_KEY")
    api_key = clean_key(raw)
    print("GROQ_API_KEY loaded:", bool(api_key))

    client = GroqClient(api_key=api_key)

    print("Using model:", client.model)
    # Use SDK-based generate: provide a system and user prompt
    system_prompt = "You are a strict JSON responder. Reply ONLY with valid JSON and nothing else."
    user_prompt = 'Reply ONLY with: {"status":"working"}'
    print("Sending prompt to model via SDK (demo/fallback disabled)...")
    try:
        out = client.generate(system_prompt, user_prompt, temperature=0.0)
        print("Raw model output (string):")
        print(out)
        try:
            parsed = json.loads(out)
            print("Parsed JSON:", parsed)
            print("SUCCESS: parsed JSON from live model")
        except Exception as e:
            print("FAILED to parse JSON from model output:", e)
    except Exception as e:
        print("Error calling Groq SDK:", e)


if __name__ == "__main__":
    main()
