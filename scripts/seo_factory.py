import os
import sys

# Wrapper to call the core engine from the user's preferred path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
engine_script = os.path.join(base_dir, 'new-version-seo', 'seo-worker-engine', 'core', 'seo_factory.py')

if not os.path.exists(engine_script):
    print(f"Error: Engine not found at {engine_script}")
    sys.exit(1)

# Pass all arguments to the core engine
args = " ".join(sys.argv[1:])
os.system(f"python3 {engine_script} {args}")
