#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

-::
drive = ""
Splitpath, drive, drive
Run RunAs, %drive%\syswow64\WindowsPowerShell\v1.0\powershell.exe
Sleep, 1000
if WinExist(ahk_exe powershell.exe)
    MsgBox,, Success, Yup
Else msgbox,, Failure, NO

'::Pause, Toggle

=::ExitApp