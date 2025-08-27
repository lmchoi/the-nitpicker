import subprocess
import sys

def get_pr_diff(pr_number: str):
    command = ["gh", "pr", "diff", pr_number]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        output_string = result.stdout
        print(output_string)

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <PR_NUMBER>")
        sys.exit(1)

    pr_number = sys.argv[1]
    get_pr_diff(pr_number)

if __name__ == "__main__":
    main()
