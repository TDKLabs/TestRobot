@echo off
setlocal EnableDelayedExpansion

set REPORTDIR=reports
set ERRORSTATUS=

SET ROBOT_SYSLOG_LEVEL=TRACE
SET ROBOT_SYSLOG_FILE=syslog.txt

for /F "delims=" %%a in ('echo %* ^| grep ".txt"') do @set testfiles=%%a
rem echo. testfiles: %testfiles%
if "%testfiles%" == "" (
for /F "delims= " %%a in ('ls "TC*.txt"') do (
if "!testfiles!"=="" (set testfiles=%%a) else (set testfiles=!testfiles! %%a)
)
)

echo. ... running the following pybot testscripts: [ %testfiles% ] ...

python -m robot.run -L TRACE -d %REPORTDIR% -b debug.txt %testfiles%
if errorlevel 1 (
set ERRORSTATUS=1
echo. XXX pybot runner returned failed status XXX
)

mv syslog.txt %REPORTDIR% 2>NUL

if exist %REPORTDIR%\report.html (
start %REPORTDIR%\report.html
)

endlocal & exit /B %ERRORSTATUS%
