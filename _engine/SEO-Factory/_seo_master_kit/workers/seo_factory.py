import os
import sys
import subprocess

# Wrapper script to run the SEO Factory Worker Engine from the scripts directory
# This satisfies the user's expected path: scripts/seo_factory.py

# Get the absolute path to the real engine
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_PATH = os.path.join(BASE_DIR, 'new-version-seo', 'seo-worker-engine', 'core', 'seo_factory.py')

if __name__ == "__main__":
    if not os.path.exists(ENGINE_PATH):
        print(f"Error: Engine not found at {ENGINE_PATH}")
        sys.exit(1)
    
    # Run the engine with all passed arguments using subprocess to handle quoting correctly
    subprocess.run([sys.executable, ENGINE_PATH] + sys.argv[1:])
