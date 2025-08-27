import subprocess

def git_diff():
    command = ["git", "diff"]

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
    git_diff()

if __name__ == "__main__":
    main()
