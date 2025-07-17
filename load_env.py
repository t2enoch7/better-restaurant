import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

def load_env(dotenv_path: str = '.env'):
    env_file = Path(dotenv_path)
    if not env_file.exists():
        print(f"No {dotenv_path} file found.")
        return
    if DOTENV_AVAILABLE:
        load_dotenv(dotenv_path)
        print(f"Loaded environment from {dotenv_path} using python-dotenv.")
    else:
        # Fallback: simple manual parsing
        with open(dotenv_path) as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    key, sep, value = line.strip().partition('=')
                    if sep:
                        os.environ.setdefault(key, value)
        print(f"Loaded environment from {dotenv_path} (manual parse, install python-dotenv for best results).")

if __name__ == "__main__":
    load_env()
