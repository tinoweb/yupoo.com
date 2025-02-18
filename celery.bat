@echo off
set PYTHONPATH=%PYTHONPATH%;%cd%
celery -A app.tasks worker --loglevel=info --pool=solo
