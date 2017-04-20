@echo off

for /F "usebackq delims==" %%i IN (`pwd`) DO set CURRENTDIR=%%i 
if "%CURRENTDIR:~-1%"==" " (set CURRENTDIR=%CURRENTDIR:~0,-1%)

set SOAPSETTINGSTPL="%TOOLCHAIN%\samples\soap\soapui-settings.tpl"
set DEFAULTKEYSTORE="%TOOLCHAIN%\samples\soap\HieKeyStore.jks"
set WSISETTINGSLOC="%TOOLCHAIN%\libs\SoapUI-5.2.0\wsi-test-tools"
set HERMESJMSLOC="%TOOLCHAIN%\libs\SoapUI-5.2.0\hermesJMS"

set KEYSTOREFILE=
set KEYSTOREPASSWD=

if "%1" == "-k" (
if "%2" == "" goto:missingparam
SET KEYSTOREFILE=%~f2
)
if "%1" == "-k" shift /2

if "%1" == "-p" (
if "%2" == "" goto:missingparam
set KEYSTOREPASSWD=%2
)
if "%1" == "-p" shift /2

if not defined KEYSTOREFILE set KEYSTOREFILE=%DEFAULTKEYSTORE%
if not exist KEYSTOREFILE set KEYSTOREFILE=%DEFAULTKEYSTORE%
if not defined KEYSTOREPASSWD set KEYSTOREPASSWD=%DEFAULTKSPASSWD%


:gensoapsettings

for /F "delims=" %%a in ('echo %KEYSTOREFILE% ^| sed "s|\\|\\\\|g"') do @set KEYSTOREFILE=%%a
if "%KEYSTOREFILE:~-1%"==" " (set KEYSTOREFILE=%KEYSTOREFILE:~0,-1%)
for /F "delims=" %%a in ('echo %WSISETTINGSLOC% ^| sed "s|\\|\\\\|g"') do @set WSISETTINGSLOC=%%a
if "%WSISETTINGSLOC:~-1%"==" " (set WSISETTINGSLOC=%WSISETTINGSLOC:~0,-1%)
for /F "delims=" %%a in ('echo %HERMESJMSLOC% ^| sed "s|\\|\\\\|g"') do @set HERMESJMSLOC=%%a
if "%HERMESJMSLOC:~-1%"==" " (set HERMESJMSLOC=%HERMESJMSLOC:~0,-1%)

echo.[keystore]: (%KEYSTOREFILE%)
echo.[passwd]: (%KEYSTOREPASSWD%)
echo.[wsisettingslocation]: (%WSISETTINGSLOC%)
echo.[hermesjmslocation]: (%HERMESJMSLOC%) 

echo.... Generating soapui-settings.xml in (%CURRENTDIR%)
sed -e "s|@@SSLSETTINGSKEYSTORE@@|%KEYSTOREFILE%|" -e "s|@@SSLSETTINGSKEYSTOREPASSWD@@|%KEYSTOREPASSWD%|" -e "s|@@WSISETTINGSLOCATION@@|%WSISETTINGSLOC%|" -e "s|@@HERMESJMSLOC@@|%HERMESJMSLOC%|" %SOAPSETTINGSTPL% > soapui-settings.xml

echo.... Done.
goto:end

:missingparam
echo.Usage: %~n0 [-k keystorefile] [-p keystorepassword]
echo.

:end
