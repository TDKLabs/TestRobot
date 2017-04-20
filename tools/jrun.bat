@echo off
setlocal EnableDelayedExpansion

echo. *** [JAVA_HOME = %JAVA_HOME%] [JDK_HOME = %JDK_HOME%] ***

set CLASSPATH="
for /F "delims=" %%a in ('dir /b /s %TROBOT%\libs\java\*.jar %TROBOT%\libs\webdriver\*.jar jars\*.jar') do (
set CLASSPATH=!CLASSPATH!;%%a
)
set CLASSPATH=!CLASSPATH!;"

echo. *** [CLASSPATH] : !CLASSPATH! ***

cmd /c groovy -cp %CLASSPATH% %*
set ERRORSTATUS=%ERRORLEVEL%

echo. @@@ groovy return code: [%ERRORSTATUS%] @@@  

:end
endlocal & exit /B %ERRORSTATUS%