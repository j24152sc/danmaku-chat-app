@echo off

start cmd /k ".venv\Scripts\activate && python server.py"

timeout /t 1 > nul

start cmd /k ".venv\Scripts\activate && python overlay.py"

timeout /t 1 > nul

start cmd /k ".venv\Scripts\activate && python client_sender.py"