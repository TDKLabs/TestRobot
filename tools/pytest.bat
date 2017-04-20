@echo off
setlocal

set REPORTDIR=results
set ERRORSTATUS=

:preclean
rm -rf %REPORTDIR% 2>NUL

for /F "delims=" %%a in ('echo %* ^| grep ".py"') do @set testfiles=%%a
rem echo. testfiles: %testfiles%
if not "%testfiles%" == "" (
echo. ... running the following user-specified test scripts: [ %* ] ...
python -m pytest -s -v %*
if errorlevel 1 (
set ERRORSTATUS=1
)
) else (
echo. ... running all test scripts in the following folder: [ %* ] ... 
python %TOOLCHAIN%\tools\pytestloader.py %*
if errorlevel 1 (
set ERRORSTATUS=1
)
) 

rem py.test -s -v %*
rem if "%~x1" == ".py" (
rem     python -m unittest -v "%~n1"
rem ) else (
rem     python -m unittest -v "%1"
rem )

:end
rm -rf __pycache__ 2>NUL
rm -rf *.pyc 2>NUL

if exist %REPORTDIR%\report.html (
start %REPORTDIR%\report.html
)

endlocal & exit /B %ERRORSTATUS%
