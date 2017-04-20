@echo off
setlocal EnableDelayedExpansion

set MRUNNER_OUT=_mrunner_output_.txt

echo. *** [JAVA_HOME = %JAVA_HOME%] [MVN_HOME = %MVN_HOME%] ***
cmd /c mvn test -DfailIfNoTests=False %* | tee %MRUNNER_OUT%
set ERRORSTATUS=%ERRORLEVEL%
:: With Windows can't get exit status of the first job (mvn) check for [ERROR] below

echo. @@@ mvn return code: [%ERRORSTATUS%] @@@  

if not exist %MRUNNER_OUT% (
	echo "XXX FATAL: (%MRUNNER_OUT%) not present - tee output missing. XXX"
	goto end
)

:: errors / failures both set error status to 1

set RE='^\[ERROR\] .*'
for /F "delims=" %%i in ('grep "ERROR" %MRUNNER_OUT% ^| tail -1 ^|python -c "import re,sys;m=re.compile(%RE%).match(sys.stdin.read());print m.group() if m else 0"') do set MVN_ERRORS=%%i
if not "%MVN_ERRORS%" == "0" (
	echo Found maven errors: %MVN_ERRORS%
	set ERRORSTATUS=1
	goto end
)

set RE='.*Failures: *(\d+)'
for /F "delims=" %%i in ('grep "Failures:" %MRUNNER_OUT% ^| tail -1 ^| python -c "import re,sys;m=re.compile(%RE%).match(sys.stdin.read());print m.groups()[0] if m else 0"') do set MRUNNERFAILURES=%%i
if not "%MRUNNERFAILURES%" == "0" (
	echo Found failures: %MRUNNERFAILURES%
	set ERRORSTATUS=1
)

echo. ### mvnrunner return code: [%ERRORSTATUS%] ###


:end
endlocal & exit /B %ERRORSTATUS%