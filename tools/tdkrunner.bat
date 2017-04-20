@echo off
setlocal

SET SELENIUM_SERVER_JAR=%TROBOT%\libs\webdriver\selenium-server-standalone-2.39.0.jar
SET ROBOT_SYSLOG_LEVEL=INFO
SET ROBOT_SYSLOG_FILE=robot_syslog.txt
set ROBOT_REPORTDIR=robot_reports
set ROBOT_DEBUGFILE=robot_debug.txt
set NO_SOAPUI_REPORT=1

if defined DEBUG (
winpdb %TOOLCHAIN%\tools\tdkrunner.py %*
goto:cleanup
)

if not defined PROFILE (
python %TOOLCHAIN%\tools\tdkrunner.py %*
) else ( 
python -m cProfile -o profile.trace %TOOLCHAIN%\tools\tdkrunner.py %*
)

:cleanup runner droppings
rm -rf __pycache__ *.pyc 2>NUL
endlocal