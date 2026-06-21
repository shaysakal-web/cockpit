' Double-click to start Cockpit Run Desk and open the browser (no terminal window).

Set shell = CreateObject("WScript.Shell")
root = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = root
shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & root & "\start_run_desk.ps1""", 0, False
