
if exist .venv\ (
    .venv\Scripts\activate.bat
) else (
    python -m venv .venv
    .venv\Scripts\activate.bat
    pip install -r requirements.txt
)

reflex run