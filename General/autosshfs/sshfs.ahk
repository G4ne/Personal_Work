#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

MsgBox, 4, Computer Owner, Does the computer you wish to mount a drive from have the same Microsoft account attached to it?
IfMsgBox No ;if you plan on mounting a drive from a computer with a microsoft account that is not yours, it will require a separate set of info. This gets that
{
    InputBox, mounteduname, Username, Please enter the username of the Microsoft account attached to the computer you wish to mount the drive from.
    Sleep, 250
    InputBox, mountedpassword, Password, Please enter the password of the Microsoft account attached to the computer you wish to mount the drive from.
    Sleep, 500
}
InputBox, uname, Username, Please enter your computer's Microsoft account username
InputBox, password, Password, Please enter your computer's Microsoft account password, hide
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
Send net use R: \\sshfs.r\%uname%@%contact%
Sleep, 500
Send {Return}
Sleep, 500
MsgBox, 4, Username and Password, Do you need to input your Username and Password?
IfMsgBox, Yes {
    
    Sleep, 1500
    Send %uname%
    Sleep, 150
    Send {Return}
    Sleep, 250
    Send %password%
    Sleep, 500
    Send {Return}
}
Sleep, 500
WinClose, ahk_exe powershell.exe

ExitApp, 0

=::ExitApp