import os
import logging
from jira import JIRA
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()

def debug_jira():
    server = os.getenv("JIRA_SERVER")
    user = os.getenv("JIRA_USER")
    token = os.getenv("JIRA_API_TOKEN")

    print(f"DEBUG: JIRA_SERVER from env is: '{server}'")
    print(f"DEBUG: JIRA_USER from env is: '{user}'")
    # Mask token
    masked_token = f"{token[:4]}...{token[-4:]}" if token and len(token) > 8 else "INVALID"
    print(f"DEBUG: JIRA_API_TOKEN is: '{masked_token}'")

    if not server or not token:
        print("Missing server or token.")
        return

    print("\nAttempting connection with token_auth...")
    try:
        jira = JIRA(server=server, token_auth=token)
        # Force a request
        myself = jira.myself()
        print(f"SUCCESS: Connected as {myself['displayName']}")
    except Exception as e:
        print(f"ERROR: {e}")
        if hasattr(e, 'response'):
            print(f"Response Status: {e.response.status_code}")
            print(f"Response Content (First 500 chars):\n{e.response.text[:500]}")
        else:
            print("No response object attached to exception (might be JSON decode error during parsing).")

if __name__ == "__main__":
    debug_jira()
