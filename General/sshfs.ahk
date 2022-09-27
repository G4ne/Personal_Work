#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.


InputBox, uname, Username, Please enter your computers username
InputBox, password, Password, Please enter your account's password, hide
RunAs, %uname%, %password%
try {
    Run C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
} catch {
    MsgBox,, Error, Invalid Information Input
    ExitApp, -1
}
loop {
    if WinExist(ahk_exe powershell.exe) {
        MsgBox,,Success, Confirmed
        Break
    }
}


'::Pause, Toggle

=::ExitApp