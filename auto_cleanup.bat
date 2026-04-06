@echo off
echo 🧹 Auto Chrome Profile Cleanup - Running every 30 minutes
:loop
echo [%date% %time%] Starting cleanup...
python cleanup_profiles.py --hours 24
echo [%date% %time%] Cleanup complete. Sleeping 30 minutes...
timeout /t 1800 /nobreak
goto loop

