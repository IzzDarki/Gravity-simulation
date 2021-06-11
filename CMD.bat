@echo off
title Command Prompt Batch 

ver
echo Henlo
echo.
:Loop
set /P the="%cd%>"
%the%
echo.
goto loop
