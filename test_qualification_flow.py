from dotenv import load_dotenv
import os, json
from utils.session_store import SessionStore
from agents.qualification_agent import QualificationAgent
from utils.groq_client import GroqClient

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = GroqClient(api_key=api_key)
store = SessionStore(session_id='manual_test')
qual = QualificationAgent(client=client, memory=store)

msgs = [
    "Hi, I'm interested in your product.",
    "We are an e-commerce retailer.",
    "About 20.",
]

for m in msgs:
    print('\nUSER:', m)
    out = qual.handle(m)
    print('AGENT_NEXT_QUESTION:', out.get('next_question'))
    print('COLLECTED:', json.dumps(out.get('collected_data'), indent=2))
    print('MISSING:', out.get('missing_fields'))
    print('QUAL_COMPLETE:', out.get('qualification_complete'))
    print('STORE FILE:', store.path)
    with open(store.path, 'r') as f:
        print('STORE CONTENT:', f.read())
