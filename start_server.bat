@echo off
cd /d "E:\project_A"
call venv\Scripts\activate.bat
cd app
python main.py
pause 