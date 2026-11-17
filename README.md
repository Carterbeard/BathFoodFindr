# BathFoodFindr

A local prototype for publishing and browsing surplus food offers on campus.

## Run locally on Mac

Install Python 3 if needed, then open the BathFoodFindr folder in VS Code.
Choose **Terminal → New Terminal** and run these commands one at a time:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python init_db.py
./.venv/bin/python -m flask --app app run --debug
```

Open http://127.0.0.1:5000/ and choose **Staff** to publish an offer
or **Student** to browse available offers. Keep the terminal running while
using the app. Press **Control+C** in the terminal to stop it.

### Start the app again later

Open a terminal in the project folder and run:

```bash
./.venv/bin/python -m flask --app app run --debug
```

### If port 5000 is already in use

Run on port 5001 instead:

```bash
./.venv/bin/python -m flask --app app run --debug --port 5001
```

Then open http://127.0.0.1:5001/.

## Run locally on Windows

Open PowerShell in the project folder and run these commands one at a time:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe init_db.py
.\.venv\Scripts\python.exe -m flask --app app run --debug
```

Open http://127.0.0.1:5000/ and choose **Staff** to publish an offer
or **Student** to browse available offers.
