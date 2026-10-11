import os
import subprocess
import sys
import json
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ML_DIR = WORKSPACE_ROOT / "backend" / "ml"
METADATA_FILE = BACKEND_ML_DIR / "kernel-metadata.json"

def main():
    print("=== Kaggle Training Deployment Script ===")
    
    # 1. Ask for Kaggle Username if not set in metadata
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
        
    username_placeholder = "<YOUR_KAGGLE_USERNAME>"
    
    if username_placeholder in metadata["id"]:
        print("Kaggle Username is not set in kernel-metadata.json.")
        kaggle_username = os.environ.get("KAGGLE_USERNAME") or input("Enter your Kaggle Username: ").strip()
        if not kaggle_username:
            print("Error: Username cannot be empty.")
            sys.exit(1)
            
        # Update metadata.json
        metadata["id"] = metadata["id"].replace(username_placeholder, kaggle_username)
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Updated kernel-metadata.json with username: {kaggle_username}")
    else:
        kaggle_username = metadata["id"].split("/")[0]

    # 2. Keep credentials in process environment; never write them to disk.
    kaggle_key = os.environ.get("KAGGLE_KEY") or input("Enter your Kaggle API Key: ").strip()
    if not kaggle_key:
        print("Error: Kaggle API key cannot be empty.")
        sys.exit(1)
    
    # 3. Set Environment Variables for Kaggle API
    os.environ["KAGGLE_USERNAME"] = kaggle_username
    os.environ["KAGGLE_KEY"] = kaggle_key
    
    # 4. Push to Kaggle
    print(f"\nPushing notebook from {BACKEND_ML_DIR} to Kaggle...")
    try:
        # Do not install packages automatically; use the caller's environment.
        result = subprocess.run(
            [sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(BACKEND_ML_DIR)],
            check=True,
            text=True,
            capture_output=True
        )
        print("\nSuccess! Notebook has been pushed and is running.")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] Failed to push to Kaggle:")
        print(e.stderr if e.stderr else e.output)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
