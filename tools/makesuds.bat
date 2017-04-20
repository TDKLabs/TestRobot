@echo off
setlocal 

if not defined SOAPUI_LOGSDIR @set SOAPUI_LOGSDIR=soapui_logs
if not defined SOAPUI_DROPPINGS @set SOAPUI_DROPPINGS=global-groovy.log soapui-errors.log soapui.log

set ERRORSTATUS=

echo. *** [I] Lathering ***

rem generate soapui project xmls for automation runner
call lather %1 %2 %*
if errorlevel 1 (
set ERRORSTATUS=1
goto:bye
)

if exist AXML.bat (
call AXML
) else (
goto:bye
)

:pre-rinse
rm -rf %SOAPUI_DROPPINGS% 2>NUL

rem run soaprunner .. the actual test
call soaprunner %AXML%
if errorlevel 1 (
set ERRORSTATUS=1
)

if defined ERRORSTATUS (
echo.  !!! WARNING : soaprunner returned an error status. !!!
)

set AXML = 
rm -f AXML.bat

if defined NO_SOAPUI_REPORT goto:rinse

rem create build.xml for ant 
if not exist %SOAPUI_LOGSDIR%\NUL goto:rinse

> build.xml (
 @echo.^<project name="report" default="report" basedir="."^>
 @echo.    ^<target name="report"^>
 @echo.       ^<junitreport todir="%SOAPUI_LOGSDIR%"^>
 @echo.           ^<fileset dir="%SOAPUI_LOGSDIR%" includes="TEST*.xml"/^>
 @echo.           ^<report format="frames" todir="%SOAPUI_LOGSDIR%"^>
 @echo.               ^<param name="TITLE" expression="SoapUI Test Results."/^>
 @echo.           ^</report^> 
 @echo.       ^</junitreport^>
 @echo.   ^</target^>
 @echo.^</project^>
)
call ant -q 1>NUL
if errorlevel 1 goto:rinse

:rinse
echo. *** [II] Rinsing  ***
rm -f build.xml
:: Move soapui droppings into SOAPUI_LOGSDIR
rem mv %SOAPUI_DROPPINGS% %SOAPUI_LOGSDIR% 2>NUL
rem mv *.log* %SOAPUI_LOGSDIR% 2>NUL


rem move all axml files into logs folder
mv "*.axml" %SOAPUI_LOGSDIR% 2>NUL

:end

if not defined NO_SOAPUI_REPORT (
if exist %SOAPUI_LOGSDIR%\index.html start %SOAPUI_LOGSDIR%\index.html
)

:bye

endlocal & exit /B %ERRORSTATUS%