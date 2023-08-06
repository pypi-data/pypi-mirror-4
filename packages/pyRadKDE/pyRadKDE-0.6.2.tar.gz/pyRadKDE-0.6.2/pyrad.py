#!/usr/bin/env python
# encoding: utf-8

"""pyRadKDE - a wheel type command interface for KDE, inspired by Kommando (KDE 3) and Neverwinternights.
"""

# additional documentation - gets added to the docstring by hand, so I can more easily use it in user output

__install__ = """
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

"""

__usage__ = """
usage:

- call "pyrad.py" to start and show pyRad and "pyrad.py --quit" to shutdown the process in the background. "pyrad.py --help" shows the usage. "pyrad.py --daemon" starts pyRad without showing the GUI.
- In systemsettings add the mouse gesture to call D-Bus: Program: org.kde.pyRad ; Object: /MainApplication ; Function: newInstance
- Use your gesture to call up the command wheel when you want to call one of your included programs.
- Left-click the program to start it. You can also press the key shown in the programs tooltip for the same effect. 
- Right-click an item to edit it. Middle-click an item to add a new one after it (clockwise).
- Make folders by clicking on the folder button and saving the item.Remove items by clicking on the delete button and saving the item. Actions are simply the commands you'd use on the commandline (there's no shell scripting though, except via `bash -c "for i in 1 2 3; do echo $i; done"`).

"""

__plans__ = """
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
"""
__ideas__ = """
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
"""

__doc__ += __install__ + __usage__ + __plans__ + __ideas__


### Basic Data ###

__copyright__ = """pyRad - a wheel type command menu.

    Copyright (c) 2009 Arne Babenhauserheise
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

### Constants ###

#: The PyRad version identifier
__version__ = "0.6.2"
appName = "pyRad"

### Commandline handling ###
# we do this here to have the maximum reaction time. 
from sys import argv
if __name__ == "__main__" and "--help" in argv:
    print __usage__
    exit()

### Imports ###

# First the GUI class and the Data about the program
# we use an import function, so we can easily delay the import.
def importRad():
    """Import the Rad GUI."""
    from rad import Rad
    return Rad

def programIcon():
    from rad import PROGRAM_ICON
    return PROGRAM_ICON

# We also do the other imports in functions to facilitate profiling. 
# Then commandline arguments and handling
from PyKDE4.kdecore import KCmdLineArgs, KCmdLineOptions

# And AboutData - moved here, so we don't need to pull in GUI stuff to check if we're the first instance
from PyKDE4.kdecore import ki18n, KAboutData

# KApplication for basics
from PyKDE4.kdeui import KUniqueApplication, KStatusNotifierItem #, KSessionManager # for handling sessions by hand, should quit not work.

# SIGNALs and SLOTs for a clean shutdown. 
from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4 import QtGui

# and exiting.
from sys import exit as exit_

### Class for modifying KUniqueApplication ###

class KUniqueCaller(KUniqueApplication):
    def __init__(self, *args, **kwds):
        """Initialize the App and import all GUI elements.

        This gets only called when there's no already existing instance of the app."""
        super(KUniqueCaller, self).__init__(*args)
        # And get and show the GUI
        Rad = importRad()
        self.rad = Rad()
        # and a tray icon
        self.statusnotifier = KStatusNotifierItem(self.rad)
        self.statusnotifier.setCategory(0) # 0 = ApplicationStatus
        self.statusnotifier.setIconByName(programIcon())
        
        #self.connect(self, SIGNAL("shutDown()"), self.quit)
        #self.connect(self, SIGNAL("quit()"), self.quit)
        #self.connect(QtGui.qApp, SIGNAL("quit()"), self.quit)
        #self.connect(self.rad, SIGNAL("queryClose()"), self.close)

    def quit(self):
        """Quit the program: close the rad, then quit."""
        try:
            self.close()
            del self.rad
        except AttributeError: 
            # quit called on the commandline, so the rad does not
            # exist for this instance.
            pass
        super(KUniqueCaller, self).quit()

    def close(self):
        """Slot for closing the rad."""
        self.rad.close()
            

    def newInstance(self):
        """Get a new instance -> in reality only check if there's already an instance and tell the GUI to run."""
        # if we get the quit arg ("pyrad.py --quit"), we close and shutdown
        args = KCmdLineArgs.parsedArgs()
        if args.isSet("quit") or args.isSet("kill"):
            self.quit()
            return 0
        elif args.isSet("daemon") or args.isSet("start"): 
            ret = super(KUniqueCaller, self).newInstance()
            return ret
        self.rad.setup()
        self.rad.show()
        self.rad.toForeground() # this cost about 0.07s
        ret = super(KUniqueCaller, self).newInstance()
        #self.rad.close() # uncomment for profiling
        return ret

### Runner ###

### About the Program ###

# This also allows our users to use DrKonqui for crash recovery.

def createAboutData():
    """Create the aboutData for PyRad."""
    #appName     = "pyRad"
    catalog     = ""
    programName = ki18n ("Rad")
    version     = __version__
    description = ki18n ("A simple radial command menu - best called with a gesture")
    license     = KAboutData.License_GPL
    copyright   = ki18n ("(c) 2009 Arne Babenhauserheide")
    text        = ki18n ("pyRad is heavily inspired by Kommando, which sadly didn't make it into KDE4. Kommando in turn was inspired by the Neverwinternights menu.")
    homePage    = "draketo.de/light/english/pyrad"
    bugEmail    = "arne_bab@web.de"

    aboutData   = KAboutData (appName, catalog, programName, version, description,
                        license, copyright, text, homePage, bugEmail)
    return aboutData

def initKApp():
    """Initialize the KApplication."""
    # First we need the aboutData
    aboutData = createAboutData()
    # Now we need to compile the commandline args for KDE programs
    KCmdLineArgs.init (argv, aboutData)
    # Add an option to quit the app
    opts = KCmdLineOptions()
    opts.add("quit", ki18n("Shutdown the background program"))
    opts.add("kill", ki18n("Shutdown the background program"))
    opts.add("daemon", ki18n("Start the background program without showing the GUI "))
    opts.add("start", ki18n("Start the background program without showing the GUI "))
    KCmdLineArgs.addCmdLineOptions(opts)
    # Then do basic initializing
    app = KUniqueCaller()
    # And get and show the GUI
    return app

def run():
    """Start and run the PyRad - and let it die"""
    # first we 
    app = initKApp()
    # Now we execute the program
    res = app.exec_()
    # Afterwards we quit explicitely. This closes and deletes the rad
    # to avoid crashing on quit and logout. FIXME: This feels wrong...
    app.quit()
    # finally return the exit code from the program.
    return res


### Self Test == Run the Program ###

if __name__ == "__main__":
    # CherryPy for finding the memory leak 
    # import cherrypy
    # from dowser import *
    # cherrypy.quickstart(Root())
    exit_(run())
