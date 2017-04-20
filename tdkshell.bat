@echo off
COLOR 2F


set drive=%~dp0
set drivep=%drive%
if #%drive:~-1%# == #\# set drivep=%drive:~0,-1%

set TOOLCHAIN=%drivep%
set TROBOT=%TOOLCHAIN%
set PATH=%drivep%\win\python\;%drivep%\tools\;%drivep%\win\python\Scripts;%drivep%\libs\SoapUI-5.2.0\bin;%drivep%\libs\groovy-2.2.2\bin;%PATH%
set WEBDRIVER_PATH=%TROBOT%\libs\webdriver
set PATH=%PATH%;%WEBDRIVER_PATH%
set PYTHONPATH=%drivep%\libs\tdklabs
set PYTHONEXE=%drivep%\win\python\python.exe
set PYTHONHOME=%drivep%\win\python
set GROOVY_HOME=%drivep%\libs\groovy-2.2.2
set FF_PATH=%drivep%\libs\ff-32.0.3

set TERM=dumb
rem avoid collisions with other perl stuff on your system
set PERL_JSON_BACKEND=
set PERL_YAML_BACKEND=
set PERL5LIB=
set PERL5OPT=
set PERL_MM_OPT=
set PERL_MB_OPT=

echo.
echo. ----------------------------------------------
echo.           TDK TestROBOT
echo.
type logo.txt
echo.
type readme.txt
echo.
echo. ----------------------------------------------
echo.

for /F "delims=" %%a in ('echo %PYTHONEXE% ^| sed "s|\\|\\\\|g"') do @set PYTHONEXE=%%a

for /F %%f in ('findstr /M "@@PYTHONEXE@@" win\python\Scripts\*.py*') do (
sed -i -e "1 s/@@PYTHONEXE@@/%PYTHONEXE%/" %%f
echo		... done patching %%f ...
del /q "sed*" 2>NUL
)

:JRE_CHECK
if not exist "%drivep%\jre\jre6" (
echo.  Unzipping jre.bin ....
unzip -q "%drivep%\jre\jre6.zip" -d %drivep%\jre
echo.  ... done unpacking jre
) 

:SOAPUI_CHECK
if not exist "%drivep%\libs\SoapUI-5.2.0" (
echo.  Unzipping SoapUI-5.2.0 ....
unzip -q "%drivep%\libs\SoapUI-5.2.0.zip" -d %drive%\libs
echo.  ... done unpacking soapui
)

:GROOVY_CHECK
if not exist "%drivep%\libs\groovy-2.2.2" (
echo.  Unzipping groovy-2.2.2 ....
unzip -q "%drivep%\libs\groovy-2.2.2.zip" -d %drive%\libs
echo.  ... done unpacking groovy 
)

:FF_CHECK
if not exist "%drivep%\libs\ff-32.0.3" (
echo.  Unzipping firefox-32.0.3 ....
unzip -q "%drivep%\libs\ff-32.0.3.zip" -d %drive%\libs
echo.  ... done unpacking firefox
)

:VERSION_NUMBER
if not exist "%drivep%\BUILD_ID" (
title TestROBOT Console - [TRUNK]
GOTO END
)


for /F "delims=" %%n in ('awk "NR==2" "%drivep%\BUILD_ID"') do @set TestROBOT_VERSION=%%n
title TestROBOT Console - Build #: [%TestROBOT_VERSION%]

:END

echo.
echo.

cmd /k
