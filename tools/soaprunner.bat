@echo off
setlocal DisableDelayedExpansion
rem NOTE: EnableDelayedExpansion instructs cmd to recognise the syntax !var! which accesses the current value of 'var'. Any variable with value(s) containing exclamation mark is not accepted.


echo. *** soaprunner.bat called with params: [ %* ] ***

set SOAPUI_HOME=%TOOLCHAIN%\libs\Soapui-5.2.0\bin
set CLASSPATH=%SOAPUI_HOME%\soapui-5.2.0.jar;%SOAPUI_HOME%\..\lib\*;
rem set CLASSPATH=%SOAPUI_HOME%\soapui-5.2.0.jar;%SOAPUI_HOME%\..\lib\*;%SOAPUI_HOME%\ext\*;
set JAVA_OPTS=-Xms128m -Xmx512m -Dsoapui.logroot="%SOAPUI_LOGSDIR%\\" -Dsoapui.properties=soapui.properties -Dsoapui.home="%SOAPUI_HOME%" -Dsoapui.ext.libraries="%SOAPUI_HOME%\ext"
rem set JAVA_OPTS=-Xms128m -Xmx1024m -Dsoapui.properties=soapui.properties -Dsoapui.home="%SOAPUI_HOME%" -Dsoapui.ext.libraries="%SOAPUI_HOME%\ext" -Dsoapui.ext.listeners="%SOAPUI_HOME%\listeners" -Dsoapui.ext.actions="%SOAPUI_HOME%\actions" 
set JAVA=java 
set SOAPUI_ERRORS_LOG=soapui-errors.log
set ERRORSTATUS=

if not exist "%SOAPUI_SETTINGS%" (call soapsettings)

:: handle multiple project files, error and exception handling ... 
for %%F in (%*) do (
rem copy /y nul __output.txt__
rem python %TOOLCHAIN%\tools\expand_soap_params.py %%F >> __output.txt__

echo.  @@@ Running SoapUITestCaseRunner with param [%%F] @@@
echo.  %JAVA% %JAVA_OPTS% com.eviware.soapui.tools.SoapUITestCaseRunner -r -a -j -M -f %SOAPUI_LOGSDIR% %DB_PROPERTIES% -t soapui-settings.xml %%F
%JAVA% %JAVA_OPTS% com.eviware.soapui.tools.SoapUITestCaseRunner -r -a -j -M -f %SOAPUI_LOGSDIR% %DB_PROPERTIES% -t soapui-settings.xml %%F
if errorlevel 1 (
:: this errorlevel check is not a conclusive check for soapui error(s). must still check for soapui-errors.log !!!
echo.  ERROR: [%%F] SoapUITestCaseRunner returned errorlevel [1]
set ERRORSTATUS=1
)

:: since soapui is not very good at reporting error(s) as return code(s) we have to take extra step to check soapui-errors.log to see if any error(s) really occurred
for /F "delims=" %%A in ('wc -l %SOAPUI_LOGSDIR%\%SOAPUI_ERRORS_LOG% 2^>NUL ^| awk "{print $1}"') do (
if "%%A" NEQ "0" (
set ERRORSTATUS=1
echo.  ERROR: [%%F] tripped SoapUITestCaseRunner - stack trace in [%SOAPUI_ERRORS_LOG%] 
)
)

rem mv %SOAPUI_DROPPINGS% "%SOAPUI_LOGSDIR%" 2>NUL
)
:: end of for

if defined ERRORSTATUS (goto:error) else (goto:end)

:error
echo.  XXX ERROR: SoapUITestCaseRunner returned an error status. XXX

:end

rm -f soapui-settings.xml
endlocal & exit /B %ERRORSTATUS%