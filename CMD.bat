@echo off
title Command Prompt Batch 
ver
echo Copyright (c) Only Keiths Cmd.
echo.
:Loop
set /P the="%cd%>"
%the%
echo.
goto loop