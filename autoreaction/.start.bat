@echo off
setlocal

REM Check if requirements.txt exists
if exist requirements.txt (
	echo Checking if all dependencies from requirements.txt are installed...
	
	REM Get the list of installed packages
	pip freeze > installed_packages.txt

	REM Install missing packages
	for /f "tokens=*" %%i in (requirements.txt) do (
		findstr /i "%%i" installed_packages.txt >nul
		if errorlevel 1 (
			echo Installing %%i...
			pip install %%i
		) else (
			echo %%i is already installed.
		)
	)

	del installed_packages.txt
) else (
	echo requirements.txt not found.
)

REM Run the main.py script using the python interpreter from the virtual environment
cls
echo Running main.py...
python main.py

endlocal
pause
