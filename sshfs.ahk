#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.


InputBox, uname, Username, Please enter your computers username
InputBox, password, Password, Please enter your account's password, hide
RunAs, %uname%, %password% ;sets user as admin with above login info
try {
    Run C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
} catch {
    MsgBox,, Error, Invalid Information Input ;throws error message and closes app if input info does not have admin privliges
    ExitApp, -1
}
loop { ;loop waiting for powershell to open, continuing script after it is open
    if WinExist(ahk_exe powershell.exe) { ;FIXME
        MsgBox,,Success, Confirmed
        Break
    }
}


'::Pause, Toggle

=::ExitApp