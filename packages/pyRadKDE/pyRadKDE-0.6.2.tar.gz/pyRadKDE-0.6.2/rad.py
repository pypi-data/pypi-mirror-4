#!/usr/bin/env python
# encoding: utf-8

"""Rad - the PyQt4 wheel Gui for pyRad"""

### Imports ###

#import objgraph# find memleaks

# First the basic python stuff
# for starting programs
import subprocess

# basics, currently only for prefix
import sys, os
# For circles
from math import sin, cos, pi
# and parsing a command string into words for Popen
from shlex import split as split_action
# Finally some path tools for loading a config file
from os.path import join, isfile, dirname

# and system independent home folder location
from user import home

# and a webbrowser
import webbrowser

# basic graphical stuff
from PyQt4.QtGui import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QCursor, QIcon, QLabel, QLineEdit, QPushButton, QKeySequence, QPolygon
# basic definitions and datatypes
from PyQt4.QtCore import Qt, QPointF, QPoint, SIGNAL, SLOT
from PyQt4.QtWebKit import QWebView

# Basics for KDE integration
from PyKDE4.kdeui import KIconLoader, KAction, KActionCollection, KShortcut, KShapeGesture
# And a basic dialog class for the edit item dialog.
from PyKDE4.kdeui import KDialog
# also the KWindowSystem, so we can get ourselves to the foreground
from PyKDE4.kdeui import KWindowSystem
# and internationalization
from PyKDE4.kdecore import i18n


### Constants ###

#: The name of the program - used in the window name
__appname__ = "pyRad"
WINDOW_WIDTH = 250
WINDOW_HEIGHT = 250
CIRCLE_RADIUS = 80
PROGRAM_ICON = "kreversi"
CENTER_ICON = "kreversi"
CONFIG_FILE_NAME = ".pyradrc"
DEFAULT_CONFIG = '''# v0.1 keep this line!
[
    ("''' + CENTER_ICON + '''", None), # the center item: (icon, action); action == None means "quit"
    ("terminal","konsole"), ("kontact","kontact"), ("konqueror","konqueror"), ("wesnoth-icon","wesnoth"), # normal items
    ("krita","""[("''' + CENTER_ICON + '''", None), ("amarok", "amarok"), ("gimp","gimp")]""") # a folder with the center icon and only one real item
]
'''

#: The keys for accessing pyrad element via the keyboard
SELECTION_KEYS_ORDERED = "0123456789abcdefghijklmnopqrstuvwxyz"

#: The maximum length of the shown tooltips (avoids missing tooltips when the tip is too long).
MAX_TOOL_TIP_LENGTH = 100

### Window ###

class ConfigWidget(QWidget):
    """A widget for configuring pyRad."""
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # first a layout
        self.lay = QVBoxLayout()
        self.setLayout(self.lay)
        # now the config buttons, horizontally
        self.config_layout = QHBoxLayout()
        self.config_keyboard = QPushButton("Keyboard")
        self.config_gestures = QPushButton("Gestures")
        self.config_layout.addWidget(self.config_keyboard)
        self.config_layout.addWidget(self.config_gestures)
        self.lay.addLayout(self.config_layout)
        # now a flattr line
        self.flattr_layout = QHBoxLayout()
        self.flattr_left = QLabel("""If you like
              pyRad""")
        self.flattr_left.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        #self.flattr_left.setAlignment(Qt.Right)
        self.flattr_right = QLabel("""Why don't you
Flattr me? :)""")
        # get the icon, either systemwide or local
        loader = KIconLoader()
        flattr_pix = loader.loadIcon(join(sys.prefix, "share", "pyrad", "Wikimedia_Flattr_Button.png"), 0)
        if flattr_pix.isNull():
            flattr_pix = loader.loadIcon(join(dirname(__file__), "images", "Wikimedia_Flattr_Button.png"), 0)
        if flattr_pix.isNull():
            flattr_pix = loader.loadIcon(join(dirname(__file__), "share", "pyrad", "Wikimedia_Flattr_Button.png"), 0)
        ic = QIcon(flattr_pix) # for a QPushButten
        self.flattr_icon = QPushButton()
        self.flattr_icon.setIcon(ic)
        self.flattr_layout.addWidget(self.flattr_left)
        self.flattr_layout.addWidget(self.flattr_icon)
        self.flattr_layout.addWidget(self.flattr_right)
        self.lay.addLayout(self.flattr_layout)
        self.pyrad_url = QLabel("^ <a href='http://draketo.de/light/english/pyrad'>http://draketo.de/light/english/pyrad</a> ^")
        self.lay.addWidget(self.pyrad_url)

        # connect signals
        self.connect(self.flattr_icon, SIGNAL("clicked()"), self.openFlattrUrl)
        self.connect(self.config_keyboard, SIGNAL("clicked()"), self.openShortcutConfig)
        self.connect(self.config_gestures, SIGNAL("clicked()"), self.openGesturesConfig)

    def openShortcutConfig(self):
        """Open the Keyboard Shortcut config dialog"""
        self.parent().processes.add(
            subprocess.Popen(["kcmshell4", "keys"], stdout=subprocess.PIPE, stderr=subprocess.PIPE))

    def openGesturesConfig(self):
        """Open the Keyboard Shortcut config dialog"""
        self.parent().processes.add(
            subprocess.Popen(["kcmshell4", "khotkeys"], stdout=subprocess.PIPE, stderr=subprocess.PIPE))

    def openFlattrUrl(self):
        """Open the flattr Url for the pyrad."""
        self.openUrl("http://flattr.com/thing/58752/pyRad-a-wheel-type-command-interface-for-KDE")
    
    def openUrl(self, url):
        """open a given URL in the browser"""
        webbrowser.open(url)

class ConfigEditor(KDialog):
    """edit the base config"""
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # Add the ConfigWidget
        self.main = ConfigWidget(self)
        self.setMainWidget(self.main)
        self.setCaption("configure the Rad")
        
    def config(self):
        """Show and raise the config dialog."""
        self.show()
        self.raise_()
        self.activateWindow()
        # run it, but don’t do anything with the result. 
        if self.exec_() == self.Accepted:
            return
        

class ItemEditWidget(QWidget):
    def __init__(self, parent=None, icon="konqueror", action=None):
        QWidget.__init__(self, parent)
        # First add a Layout
        self.lay = QGridLayout()
        self.setLayout(self.lay)
        # Now add a description text
        self.description = QLabel("Edit the icon (KDE progam name) and the action (commandline input).")
        self.lay.addWidget(self.description, 0, 0, 1, 3)
        # Then add a text field with name        
        self.icon_label = QLabel("Icon:", self)
        self.icon_edit = QLineEdit(self)

        # and the icon, updated live
        self.iconloader = KIconLoader()
        #self.icon = QPushButton(self) # for a button
        self.icon = QLabel(self)
        self.icon.icon = icon
        self.icon.action = action

        self.lay.addWidget(self.icon_label, 1, 0)
        self.lay.addWidget(self.icon_edit, 1, 1, 1, 2)
        self.lay.addWidget(self.icon, 1, 3)
        # Also add the same for the action
        self.action_label = QLabel("Action:", self)
        self.action_edit = QLineEdit(self)
        self.action_new_folder = QPushButton("folder", self)
        self.action_delete = QPushButton("delete", self)
        self.lay.addWidget(self.action_label, 2, 0)
        self.lay.addWidget(self.action_edit, 2, 1)
        self.lay.addWidget(self.action_new_folder, 2, 2)
        self.lay.addWidget(self.action_delete, 2, 3)

        # make the icon update automatically
        self.icon_edit.connect(self.icon_edit, SIGNAL("textChanged(QString)"), self.reload_icon)
        # action buttons
        self.action_new_folder.connect(self.action_new_folder, SIGNAL("clicked()"), self.action_to_folder)
        self.action_delete.connect(self.action_delete, SIGNAL("clicked()"), self.action_empty)
        
    def reload_icon(self, name):
        """reload the icon from the new name"""
        self.icon.icon = name
        #ic = QIcon(self.iconloader.loadIcon(name, 0)) # for a QPushButten
        #self.icon.setIcon(ic)
        self.icon.setPixmap(self.iconloader.loadIcon(name, 0))

    def action_to_folder(self):
        """turn the action into an empty folder"""
        self.action_edit.setText("[('kreversi', None)]")

    def action_empty(self):
        """turn the action into an empty folder"""
        self.action_edit.setText("")
        

# First we need a message box for editing the entries
class ItemEditor(KDialog):
    def __init__(self, parent=None):
        KDialog.__init__(self, parent)
        # First add a layout
        # Now add widgets
        self.main = ItemEditWidget(self)
        self.setMainWidget(self.main)


    def edit(self, icon, action):
        """Edit an item - includes deleting it by returning None."""
        # Show the dialog.
        self.main.icon_edit.setText(icon)
        if action is None:
            action = ""
        self.main.action_edit.setText(action)
        self.show()
        self.raise_()
        self.activateWindow()
        # And run it.

        if self.exec_() == self.Accepted:
            action = self.main.action_edit.text()
            icon = self.main.icon_edit.text()
            if action == "":
                action = None
                return str(icon), action
            return str(icon), str(action)




# We just use and extend example from TechBase
# http://techbase.kde.org/Development/Tutorials/Plasma/Python/GettingStarted

class Rad(QWidget):
    def __init__(self, parent=None, f=Qt.FramelessWindowHint):
        """Create the Window."""
        QWidget.__init__(self, parent, f)
        # Quit when this window gets closed
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Add a name
        self.setWindowTitle(__appname__)

        # And an icon
        self.iconloader = KIconLoader()
        icon = QIcon(self.iconloader.loadIcon(PROGRAM_ICON, 0))
        self.setWindowIcon(icon)

        # resize
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # add a devnull file to send process output.
        self.devnull = open(os.devnull, "wb")

        # Add a circle-list for all items
        self.circle = []

        # add a shortcut to show the Rad.
        self.showAction = KActionCollection(self).addAction("show")
        self.showAction.setHelpText(i18n("Show the PyRad"))
        short = self.showAction.shortcut()
        short.setPrimary(QKeySequence(Qt.ALT + Qt.Key_F6))
        short.setAlternate(QKeySequence(Qt.META + Qt.Key_F6))
        self.showAction.setShortcut(short)
        self.showAction.setGlobalShortcut(short)
        # p0 = QPoint(9,3)
        # p1 = QPoint(0,0)
        # poly = QPolygon()
        # poly.append(p0)
        # poly.append(p1)
        # reload_gesture = "0,0.0625,-0.5,0.5,1,0.0625,0.0625,-0.5,0.5,0.875,0.125,0.0625,-0.5,0.5,0.75,0.1875,0.0625,-0.5,0.5,0.625,0.25,0.0625,-0.5,0.5,0.5,0.3125,0.0625,-0.5,0.5,0.375,0.375,0.0625,-0.5,0.5,0.25,0.4375,0.0625,-0.5,0.5,0.125,0.5,0.0625,0.5,0.5,0,0.5625,0.0625,0.5,0.5,0.125,0.625,0.0625,0.5,0.5,0.25,0.6875,0.0625,0.5,0.5,0.375,0.75,0.0625,0.5,0.5,0.5,0.8125,0.0625,0.5,0.5,0.625,0.875,0.0625,0.5,0.5,0.75,0.9375,0.0625,0.5,0.5,0.875,1,0,0,0.5,1"
        # gest = KShapeGesture(reload_gesture)
        # gest.setShapeName("line, 1 right, 1/3rd up")
        # self.showAction.setShapeGesture(gest)
        # print self.showAction.shapeGesture().toString()
        self.showAction.connect(self.showAction, SIGNAL("triggered(Qt::MouseButtons, Qt::KeyboardModifiers)"), self.showByShortcut)

        # Setup the circle - TODO: Call it via KUniqueApplication.newInstance
        #self.setup()

    def showByShortcut(self, mouseButtons=None, KeyboardModifiers=None):
        self.setup()
        self.show()
        self.toForeground()

    def toForeground(self):
        """Get into the foreground, so the user can click us."""
        self.activateWindow()
        KWindowSystem.forceActiveWindow(self.winId())

    def setup(self): 
        """Setup the items in the circle - used to show the app anew.

        @param message: Gets the message from the uniqueCalled signal - currently just discarded.
        """
        # Move below the cursor
        self.move_to_cursor()

        # Make sure we get focus events
        self.setFocusPolicy(Qt.StrongFocus)

        # Load the items from the config file.
        items = self.load_config()

        # And arrange them as labels in a circle
        self.arrange_in_circle(items)

        # Finally add a message_box instance for editing items
        # self.message_box = KMessageBox()

        # Also we need an editor for the items. Call it with self.editor.exec(item).
        self.editor = ItemEditor(self)
        # and a config editor
        self.editor_config = ConfigEditor(self)


    def focusOutEvent(self, event):
        """Hide when we lose the focus and the mouse isn't inside the window."""
        # catch error case: don't close the window when the focus changed
        # due to becoming inactive even though the mouse is over the window.
        # Fixes the "quit when move across tooltip" bug.
        # Also fixes the "crash when mouse clicks while editor starts" bug. 
        if event.reason() == Qt.ActiveWindowFocusReason and self.isInside(QPointF(QCursor.pos()), self) or self.editor.main.isVisible():
            return None
        # if we lose focus, the wheel disappears
        self.hide()

    def mouseReleaseEvent(self, event):
        """Hide when we get a mouse release on a final item."""
        # Debug: Don't react, if an edit dialog is open.
        if self.editor.main.isVisible():
            return None
        
        #print objgraph.show_growth()

        # Get the position
        pos = event.pos()

        clicked = None
        for i in self.circle[:]:
            if self.isInside(pos, i):
                clicked = i

        if not clicked:
            # Otherwise we can hide the pyRad
            self.hide()

        # If pyRad didn't reach a final action, we stop here.
        if event.button() == Qt.LeftButton:
            if self.labelClicked(clicked) is None:
                return # TODO: Check if we can use return None instead
            else: 
                self.hide()
        elif event.button() == Qt.RightButton and clicked != self.circle[0]:
            self.editLabel(clicked)
            return
        elif event.button() == Qt.RightButton and clicked == self.circle[0]:# and i.action is None: # only in the top wheel.
            # TODO: right-click on the middle item should show the options. 
            # currently we just don't edit it. 
            self.editor_config.config()
            return
        elif event.button() == Qt.MidButton:
            self.addLabelAfter(clicked)
            return
        else: # other buttons are ignored
            return

            
    def keyReleaseEvent(self, event):
        """Select items via keyboard."""
        # Debug: Don't react, if an edit dialog is open.
        if self.editor.main.isVisible():
            return None

        key = str(event.text())
        if key and key in SELECTION_KEYS_ORDERED[:len(self.circle)]:
            idx = SELECTION_KEYS_ORDERED.index(key)
            if not self.labelClicked(self.circle[idx]) is None:
                self.hide()
	else: 
	    if event.key() == Qt.Key_Escape: 
		self.hide()
        

    def addLabelAfter(self, label): # -> open message box -> set item.icon and item.action. -> save_config()
        """Edit a label. A click on the center item promts for adding a new label."""
        # add a new label.
	item = self.editor.edit(label.icon, label.action)
	#: the place where we're in the wheel. the new label should be at idx + 1
	idx = self.circle.index(label)
	if item is None:
	    return None
	icon, action = item
	if action is None:
	    return None
	items = [(i.icon, i.action) for i in self.circle]
	items = items[:idx+1] + [(icon, action)] + items[idx+1:]
        self.save_config(items)


    def editLabel(self, label): # -> open message box -> set item.icon and item.action. -> save_config()
        """Edit a label. A click on the center item promts for adding a new label."""
        # Don't hide when the dialog pops up
	item = self.editor.edit(label.icon, label.action)
	if item is None:
	    return None # clicked cancel
	icon, action = item
	items = [(i.icon, i.action) for i in self.circle]
        idx = self.circle.index(label)
	if action is not None:
	    items[idx] = (icon, action)
	else:
	    items = items[:idx] + items[idx + 1:]
        self.save_config(items)


    def labelClicked(self, label):
        """React to a label being clicked.

        @return: True if the circle reached an end, None if it should continue existing."""
        if label.action is None:
            return True
        if label.action[0] == "[":
            # then it's a folder!
            # get its contents
            items = eval(label.action)
            # and store the current items in the new center.
            # as long as the user didn't click the center
            if not label is self.circle[0]:
                items[0] = ( CENTER_ICON , str([(i.icon, i.action) for i in self.circle]) )
            self.arrange_in_circle(items)
            # We don't do anything else in that case.
            return None
        # if it's no folder and not None, we start the program
        # if this fails, the code ends here
        # and the circle stays visible.
        if label.action is not None:
            try:
                subprocess.Popen(split_action(label.action), 
                                 stdout=self.devnull, 
                                 stderr=self.devnull)
                return True
            except:
                return None

    def isInside(self, point, thing):
        """Check, if the point is inside the thing."""
        if point.x() > thing.x() and point.x() < thing.x() + thing.width() and point.y() > thing.y() and point.y() < thing.y() + thing.height():
            return True
        else:
            return False

    def move_to_cursor(self):
        """Move the Window to the position of the mouse cursor."""
        # We set the position to the Cursor
        pos = QPointF(QCursor.pos())
        # center on the cursor (reduce by half window width and height)
        x = pos.x() - 0.5*self.size().width()
        y = pos.y() - 0.5*self.size().height()
        self.move(x, y)

    def arrange_in_circle(self, items):
        """Arrange all icons in a circle, with the zeroth in the middle."""
        # First remove the previous items
        for label in self.circle[:]:
            label.hide()
            label.close()
            label.clear()
            label.destroy()
            #print dir(label)
            #print label.parent().children()
        #print objgraph.show_growth()
        #if self.circle:
        #    objgraph.show_backrefs(self.circle[:], filename="graph.png")
        

        # Then create the circle list
        self.circle = self.items_to_circle(items)

        # Now set the center icon
        self.circle[0].move(0.5*self.width() - 0.25*self.circle[0].width(), 0.5*self.height() - 0.75*self.circle[0].height())

        # TODO: Check QPainterPath -> circle by percentage. 
        # And finally arrange all other items in a circle around the center.
        for i in self.circle[1:]:
            angle = 2 * pi * (self.circle.index(i) -1 ) / len(self.circle[1:])
	    # x is -sin(angle), so we get clockwise arrangement and a pentagramm pointing upwards ;) 
            x_displacement = -sin(angle)*CIRCLE_RADIUS
            y_displacement = cos(angle)*CIRCLE_RADIUS
            x = 0.5*self.width() - 0.25*i.width()
            y = 0.5*self.height() - 0.75*i.height()
            x += x_displacement
            y += y_displacement
            i.move(x, y)

        # Finally show the new circle
        for i in self.circle:
            i.show()

    def items_to_circle(self, items):
        """Create the circle list from the given items.
        @return: circle (list of labels)"""
        circle = []
        for icon, action in items:
            label = self.item_to_label(icon, action)
            # we set the tooltip here,
            # because it needs the position in the circle.
            if SELECTION_KEYS_ORDERED[len(circle):]: 
                key = SELECTION_KEYS_ORDERED[len(circle)]
                if action is not None and action.startswith("["):
                    toolTip =  key + " - " + "(" + ", ".join([str(act) for ico,act in eval(action) if act]) + ")"
                else: 
                    toolTip =  key + " - " + str(action)
            else:
                toolTip = str(action)
            # toolTip = toolTip.replace('"', "")
            # print(toolTip)
            if toolTip[MAX_TOOL_TIP_LENGTH:]: 
                label.setToolTip(toolTip[:MAX_TOOL_TIP_LENGTH]+"...")
            else:
                label.setToolTip(toolTip)
            circle.append(label)

        return circle

    def item_to_label(self, icon, action):
        """Turn an item into a QLabel."""
        label = QLabel(self)
        label.icon = icon
        label.action = action
        # The tooltip must be set outside this function,
        # because it needs the position in te circle. 
        # label.setToolTip(str(action))
        label.setPixmap(self.iconloader.loadIcon(icon, 0))
        return label

    def load_config(self):
        """Load the items from the config file.

        @return: items (list)"""
        # If there's no config, we use standard items
        if not isfile(join(home, CONFIG_FILE_NAME)):
            #: The items the menu should show in top-level (via folders this contains the whole of the wheel menu).
            items = eval(DEFAULT_CONFIG)
            # also create the config file -> this is an initial run
            f = open(join(home, CONFIG_FILE_NAME), "w")
            f.write(DEFAULT_CONFIG)
            f.close()
        else:
            # if a config file is present, we load the items from there.
            f = open(join(home, CONFIG_FILE_NAME))
            config = f.read()
            assert(config.startswith("# v0.1"))
            items = eval(config)
            f.close()
            del f
            del config

        return items

    def save_config(self, items):
        """Save the current wheel layout to the config file.

        @param items: The new layout at any level."""
        # We roll back the circle to the top level
        #: The trail we walked - traverse in reverse to get back to the upper layout. 
        clicktrail = [] 
        # store current items as item list
        #: The current upper layout
        items_upper = [(label.icon, label.action) for label in self.circle]
        # And reshape the circle, so it corresponds to the layout we want to save
        self.arrange_in_circle(items)
        # The center can't change, so we can use the one from the previous version of the circle.
        while self.circle[0].action is not None:
            #: Items in the current folder, not for the circle!
            items_folder = items_upper
            # replace the first with a generic center.
            items_folder[0] = ( CENTER_ICON, None )

            ## Now we switch to the lower layout!
            self.labelClicked(self.circle[0])

            # find the folder corresponding to the upper layout.
            #: the current *lower* layout
            items_lower = [(label.icon, label.action) for label in self.circle]
            found_the_folder = False
            for item in items_lower:
                icon, action = item
                if action is not None and action[0] == "[" and eval(action) == items_folder:
                    # We found the correct folder. 
                    # the index of the folder in the lower layout
                    idx = items_lower.index(item)
                    # create the new folder
                    items_folder = items[:]
                    items_folder[0] = ( CENTER_ICON, None )
                    # replace the old folder with the new folder.
                    item = (icon, str(items_folder))
                    items_lower[idx] = item
                    self.arrange_in_circle(items_lower)
                    # Also store the folder we found in the clicktrail
                    clicktrail.append(self.circle[idx])
                    found_the_folder = True
            # make sure we save no broken configs!
            if not found_the_folder:
                print "Gah!"
                return False
            # store current items as item list again
            #: The current upper layout
            items_upper = [(label.icon, label.action) for label in self.circle]


        items_new = [(i.icon, i.action) for i in self.circle]
        # Now we walk back on the clicktrail
        clicktrail.reverse()
        for label in clicktrail:
            self.labelClicked(label)
        # Finally we prepare the config data
        config = "# v0.1 keep this line!\n"
        config += str(items_new)
        # And save it
        f = open(join(home, CONFIG_FILE_NAME), "w")
        f.write(config)
        f.close()
