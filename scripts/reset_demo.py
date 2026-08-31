import os
import sys

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import reset_db

def reset_demo():
    print("Resetting RecoverAI Database...")
    reset_db()
    print("Database reset completed successfully. State is completely fresh.")

if __name__ == "__main__":
    reset_demo()
