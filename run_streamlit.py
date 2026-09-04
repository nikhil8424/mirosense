"""Simple entry point for Streamlit app."""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Run the streamlit app
if __name__ == "__main__":
    from app.streamlit_app import main
    main()