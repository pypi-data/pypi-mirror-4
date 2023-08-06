#pyRad

pyRadKDE - a wheel type command interface for KDE, inspired by Kommando (KDE 3) and Neverwinternights.

installation:

- easy_install pyRadKDE

setup: 

- Add "/usr/bin/pyrad.py" as script to your autostart (systemsettings->advanced->autostart) TODO: make it not show the GUI.
- Run "/usr/bin/pyrad.py" to see it in your current session. 
- You can now call it with Alt-F6 or Meta-F6.

set a mouse gesture: 

- Add the mouse gesture to call D-Bus: Program: org.kde.pyRad ; Object: /MainApplication ; Function: newInstance
- Alternately set the gesture to call the command "dbus-send --type=method_call --dest=org.kde.pyRad /MainApplication org.kde.KUniqueApplication.newInstance"
- customize the menu by editing the file "~/.pyradrc" or right- and middle-clicking items.


usage:

- call "pyrad.py" to start and show pyRad and "pyrad.py --quit" to shutdown the process in the background. "pyrad.py --help" shows the usage. "pyrad.py --daemon" starts pyRad without showing the GUI.
- In systemsettings add the mouse gesture to call D-Bus: Program: org.kde.pyRad ; Object: /MainApplication ; Function: newInstance
- Use your gesture to call up the command wheel when you want to call one of your included programs.
- Left-click the program to start it. You can also press the key shown in the programs tooltip for the same effect. 
- Right-click an item to edit it. Middle-click an item to add a new one after it (clockwise).
- Make folders by clicking on the folder button and saving the item.Remove items by clicking on the delete button and saving the item. Actions are simply the commands you'd use on the commandline (there's no shell scripting though, except via `bash -c "for i in 1 2 3; do echo $i; done"`).


plan:

- new command scheme: right-click always edits, middle-click adds a new item. -done
- items arranged clockwise. -done
- Edit dialog should show the icon graphically. A click on the item should show the edit dialog we have when editing the K-Menu. -done
- Edit dialog should have a radio button for the action: "create folder". -done
- register a global shortcut / gesture in KDE from within the program -> usable as soon as it's installed. -partial (keyboard: Alt-F6)
- make it show faster. -done
- add option --only-daemon to only start the daemon without showing the GUI -done
- right-click on center opens a general config dialog. -done
- a general config dialog. -done
- first run of new version shows image as usage guide. -todo

ideas:

- use plasma.
- Show the program cathegories from the K-Menu.
- Get the folders and actions from Nepomuk somehow -> favorites or such.
- Option to have an auto-optimizing wheel layout :)
- adjust icon size to the number of icons in the circle.
- Adjust circle radius to the number of icons. Or better: Use a double-cycle (so the distances are always the same and muscle memory works :) ).
- Show the icons inside a folder over/around the folder icon. 
- Add a CLI fallback, so people can also access their actions via the shell. 
- Check if an app is already open. If it is, simply switch to it (dbus -> get winID, forceActivateWindow(winID)?). 
  Sample DBus calls: dbus-send --dest=org.freedesktop.DBus --type=method_call --print-reply / org.freedesktop.DBus.ListNames ; dbus-send --dest=org.kde.konqueror-14040 --type=method_call --print-reply /konqueror/MainWindow_1 org.kde.KMainWindow.winId; dbus-send --dest=org.freedesktop.DBus --type=method_call --print-reply / org.freedesktop.DBus.NameHasOwner string:"org.kde.pyRad"
  To bring a background app to foreground, hide its main window, then show it again.
  -> /konqueror com.trolltech.Qt.QWidget.hide + ...show + hide pyRad
  PID stuff: http://code.google.com/p/psutil/
- Talk to DBus directly (for higher performance). -> dbus-send --type=method_call --dest=org.kde.pyRad /MainApplication org.kde.KUniqueApplication.newInstance
  (from http://www.staerk.de/thorsten/index.php/Hacking_KDE) -done, left here for reference to the site.

PyPI url: http://pypi.python.org/pypi/pyRadKDE
Website: http://draketo.de/light/english/pyrad
