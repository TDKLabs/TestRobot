@echo off
setlocal
python %TOOLCHAIN%\tools\lather.py %*
::echo %ERRORLEVEL%
endlocal & exit /B %ERRORLEVEL%