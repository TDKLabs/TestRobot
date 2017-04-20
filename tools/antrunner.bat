@echo off
setlocal EnableDelayedExpansion

set ARUNNER_OUT=_arunner_output_.txt

echo. *** [JAVA_HOME = %JAVA_HOME%] [ANT_HOME = %ANT_HOME%] ***

cmd /c ant %* | tee %ARUNNER_OUT%
set ERRORSTATUS=%ERRORLEVEL%

echo. @@@ ant return code: [%ERRORSTATUS%] @@@  

if not exist %ARUNNER_OUT% (
	echo "XXX FATAL: (%ARUNNER_OUT%) not present - tee output missing. XXX"
	goto end
)

:: errors / failures both set error status to 1

set RE='.*Failures: *(\d+)'
for /F "delims=" %%i in ('grep "Failures:" %ARUNNER_OUT% ^| tail -1 ^| python -c "import re,sys;m=re.compile(%RE%).match(sys.stdin.read());print m.groups()[0] if m else 0"') do set ARUNNERFAILURES=%%i
if not "%ARUNNERFAILURES%" == "0" (
	echo Found failures: %ARUNNERFAILURES%
	set ERRORSTATUS=1
)

echo. ### antrunner return code: [%ERRORSTATUS%] ###


:end
endlocal & exit /B %ERRORSTATUS%