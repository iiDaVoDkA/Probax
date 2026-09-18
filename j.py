deactivate

brew install python@3.12

mv venv venv-py311-backup

$(brew --prefix python@3.12)/bin/python3.12 -m venv venv

source venv/bin/activate

python --version

python -m pip install --upgrade pip

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000