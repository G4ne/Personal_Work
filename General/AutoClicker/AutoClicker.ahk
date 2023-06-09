#NoEnv
#SingleInstance force

clicker_on := false ;A variable to keep track of whether the autoclicker is on or off

Gui, MyGui:New ;Begin building Gui

Gui, MyGui:Margin, 35, 10

Gui, MyGui:Add, Text, x35 y10, Input the amount of miliseconds between clicks

Gui, MyGui:Add, Edit, vwait_time gsubmit_data w185 h20 x53 y34 ;Input box for the time between clicks

Gui, MyGui:Add, UpDown, w200 h30, 0 ;UpDown on the input box

Gui, MyGui:Add, Text, x50 y62, Input the start/stop key

Gui, MyGui:Add, Hotkey, vstart_key gset_hotkey w150 h20 x35 y80 ;Hotkey box used to create the hotkey from user input

Gui, MyGui:Add, Checkbox, vleft_right_click gsubmit_data x190 y70, Right Click ;Checkbox for right click vs left click (True = right click, False = left click)

Gui, MyGui:Add, Checkbox, vhold_button gsubmit_data x190 y87, Hold Button ;Checkbox for holding / not holding click (True = hold, False = don't hold)

Gui, MyGui:Add, Button, gstart_stop_click w290 h35 x5 y110, Start ;Built-in button used to start and stop the auto clicker

Gui, MyGui:Show, w300 h150 ;End building Gui and show it


=:: ;Close Script
Gui, Destroy
ExitApp


^/::WinActivate, ahk_exe AutoHotKeyU64.exe ;Bring Gui to the front


start_stop_click: ;Turns the autoclicker on when the start key is hit and turns it off if hit again
if (clicker_on == true) { ;Returns after releasing any keys that are being held down
    SetTimer, _Run, Off ;Stops the autoclicker
    GuiControl, MyGui:, Stop, Start ;Changes the text on the button to start from stop
    Send {LButton up} ;Releases pressed keys
    Send {RButton up}
    clicker_on := false
    return
}
else { ;Starts clicking using the interval from the Gui
    GuiControl, MyGui:, Start, Stop ;Changes the text on the button to stop from start
    clicker_on := true
    SetTimer, _Run, %wait_time% ;Loops _Run on a timer, clicking at the specified interval
    return
}


_Run: ;Wrapper label for the _Run function
_Run(wait_time, left_right_click, hold_button)
return


set_hotkey: ;Sets the hotkey to the given key during runtime
Gui, Submit, NoHide
Hotkey, %start_key%, start_stop_click
return


submit_data: ;Updates Gui variables with their appropriate values
Gui, Submit, NoHide
return


_Run(waittime, LR, hold) { ;The main function used to do the clicking

    if (hold == True and LR == True) { ;Holds down right click
        Send {RButton down}
        Sleep, waittime
        Send {RButton up}
    }
    else if (hold == True and not LR == True) { ;Holds down left click
        Send {LButton down}
        Sleep, waittime
        Send {LButton up}
    }
    else if (LR == True and not hold == True) { ;Presses right click
        Send {RButton}
    }
    else { ;Presses left click
        Click
    }
    return
}

GuiClose: ;Runs when the Gui is closed
ExitApp 