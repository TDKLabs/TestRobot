@echo off
setlocal EnableDelayedExpansion

:GETOPTS
if /I "%1" == "" goto Help
if /I %1 == -h goto Help
if /I %1 == --help goto Help
if /I %1 == --env set MQENV=%2 & shift
shift
if not (%1)==() (
	set SCRIPT_NAME=%1
	goto GETOPTS
)

goto start
:Help
echo.Usage: %~n0 [--env Environment to use]
echo. 
goto end
:start
if "%MQENV%" == "" goto Help

set MQENV=%MQENV: =%
set JRUNNER_OUT=_jrunner_output_.txt

echo. *** [MQENV = %MQENV%]
echo. *** [JAVA_HOME = %JAVA_HOME%] [JDK_HOME = %JDK_HOME%] ***

set CLASSPATH="
for /F "delims=" %%a in ('dir /b /s %TROBOT%\libs\java\ %TROBOT%\libs\groovy-2.2.2\lib\junit-4.11.jar %TROBOT%\libs\SoapUI-5.2.0\lib\ojdbc5.jar %TROBOT%\libs\webdriver\*.jar jars\*.jar') do (
	set CLASSPATH=!CLASSPATH!;%%a
)
set CLASSPATH=!CLASSPATH!;"

echo. *** [CLASSPATH] : !CLASSPATH! ***

cmd /c groovy -cp %CLASSPATH% %SCRIPT_NAME% | tee %JRUNNER_OUT% 
rem cmd /c groovy %*
set ERRORSTATUS=%ERRORLEVEL%

echo. @@@ groovy return code: [%ERRORSTATUS%] @@@  

if not exist %JRUNNER_OUT% (
	echo "XXX FATAL: (%JRUNNER_OUT%) not present - tee output missing. XXX"
	goto end
)

:: errors / failures both set error status to 1

set RE='.*Failures: *(\d+)'
for /F "delims=" %%i in ('grep "Failures:" %JRUNNER_OUT% ^| tail -1 ^| python -c "import re,sys;m=re.compile(%RE%).match(sys.stdin.read());print m.groups()[0] if m else 0"') do set JRUNNERFAILURES=%%i
if not "%JRUNNERFAILURES%" == "0" (
	echo Found failures: %JRUNNERFAILURES%
	set ERRORSTATUS=1
)
set RE='.*Errors: *(\d+)'
for /F "delims=" %%i in ('grep "Errors:" %JRUNNER_OUT% ^| tail -1 ^| python -c "import re,sys;m=re.compile(%RE%).match(sys.stdin.read());print m.groups()[0] if m else 0"') do set JRUNNERERRORS=%%i
if not "%JRUNNERERRORS%" == "0" (
	echo Found errors: %JRUNNERERRORS%
	set ERRORSTATUS=1
)

echo. ### jrunner return code: [%ERRORSTATUS%] ###

:end
rem del /F /Q %JRUNNER_OUT% 2>NUL
endlocal & exit /B %ERRORSTATUS%