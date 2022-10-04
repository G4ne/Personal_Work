#NoEnv
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

InputBox, uname, Username, Please enter your computer's username
InputBox, password, Password, Please enter your account's password, hide
RunAs, %uname%, %password% ;sets user as admin with above login info
try {
    Run C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
} catch {
    MsgBox,, Error, Invalid Information Input ;throws error message and closes app if input info does not have admin privliges
    ExitApp, -1
}
WinWait, ahk_exe powershell.exe ;waits for powershell window to be opened
Sleep, 1000 ;waits for powershell to initialize itself
InputBox, contact, Address, Please enter your computer's Address (Ex: 192.168.1.11 or 24.182.162.1)
Send net use R: /delete ;deletes mounted drive
Sleep, 100
Send {Return}
WinClose, ahk_exe powershell.exe

ExitApp, 0

'::Pause, Toggle
=::ExitApp