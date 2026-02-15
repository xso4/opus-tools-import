import json
import os
import subprocess
import sys

def get_remote_head(url):
    try:
        result = subprocess.run(
            ["git", "ls-remote", url, "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.split()[0]
    except Exception as e:
        print(f"Error checking {url}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    json_path = ".github/upstream-version.json"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found", file=sys.stderr)
        sys.exit(1)

    is_manual = os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
    updates_found = False
    
    print("Checking for updates...")
    
    # Prepare output file
    if "GITHUB_OUTPUT" in os.environ:
        output_file = open(os.environ["GITHUB_OUTPUT"], "a")
    else:
        output_file = sys.stdout

    for name, repo_data in data["repositories"].items():
        current_hash = repo_data["commit"]
        remote_url = repo_data["url"]
        
        print(f"Checking {name} ({remote_url})...")
        latest_hash = get_remote_head(remote_url)
        
        # Output SHA
        key = f"sha_{name.replace('-', '_')}"
        if output_file != sys.stdout:
            output_file.write(f"{key}={latest_hash}\n")
        else:
            print(f"OUTPUT: {key}={latest_hash}")
        
        if latest_hash != current_hash:
            print(f"  UPDATE FOUND: {name} {current_hash[:7]} -> {latest_hash[:7]}")
            updates_found = True
        else:
            print(f"  Up to date: {latest_hash[:7]}")

    should_run = is_manual or updates_found
    if output_file != sys.stdout:
        output_file.write(f"should_run={str(should_run).lower()}\n")
        output_file.close()
    else:
        print(f"OUTPUT: should_run={str(should_run).lower()}")
        
    print(f"\nSummary: Manual={is_manual}, Updates={updates_found} => Run={should_run}")

if __name__ == "__main__":
    main()
