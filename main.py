import json
import os
import requests
import subprocess
import sys

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_pr_diff(pr_number: str) -> str:
    command = ["gh", "pr", "diff", pr_number]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")


def get_ai_suggestions(diff) -> str:
    """
    Sends the PR context to the AI model and returns the suggested comments.
    """
    headers = {
        'Content-Type': 'application/json'
    }

    prompt = "Review the PR and nitpick, for each comment/suggestion, include file and line number"
    prompt += f"```diff\n{diff}\n```"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000,
        },
    }

    print("Sending PR content to AI for analysis...")

    try:
        response = requests.post(
            f"{API_URL}?key={GOOGLE_API_KEY}",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "No suggestions returned from the AI."
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        print(f"Response: {err.response.text}")
        sys.exit(1)
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <PR_NUMBER>")
        sys.exit(1)

    pr_number = sys.argv[1]
    pr_diff = get_pr_diff(pr_number)

    ai_suggestions = get_ai_suggestions(pr_diff)
    
    print("\n--- AI Suggested Comments ---")
    print(ai_suggestions)
    print("\n-----------------------------")
    print(f"Review the suggestions above and manually add them to PR #{pr_number}.")

if __name__ == "__main__":
    main()
