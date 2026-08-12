"""
Streamlit Cloud entry point for ASTRA Command OS.
Local dev: python main.py --desktop  or  streamlit run app.py
"""

from desktop.shell import render

if __name__ == "__main__":
    render()
