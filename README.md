# BathFoodFindr

A local prototype for publishing and browsing surplus food offers on campus.

## Run locally on Windows

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe init_db.py
.\.venv\Scripts\python.exe -m flask --app app run --debug
```

Open http://127.0.0.1:5000/ and choose Staff to publish an offer
or Student to browse available offers.