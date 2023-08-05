#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import shlex

from PyQt4 import QtCore, QtGui

from ui.main import Ui_MainWindow


class MainForm(QtGui.QMainWindow):
    FIFO_REFRESH_TIMEOUT = 100
    
    def __init__(self, app):

        self.app = app
        super(MainForm, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        # centering on the desktop

        desktop = self.app.desktop().screenGeometry()
        
        x = (desktop.width() - self.window().width()) / 2
        y = (desktop.height() - self.window().height()) / 3
        
        self.move(x, y)
        
        
        self.connect(self.ui.runButton, QtCore.SIGNAL("clicked()"), self.run)
        self.connect(self.ui.command, QtCore.SIGNAL("editTextChanged(QString)"), self.command_changed)
        
        self.commands = []
        self.config_load()

    def config_init(self):
        path = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'altf2')
        if not os.path.exists(path):
            os.makedirs(path)
            
        filename = os.path.join(path, 'history')
        if not os.path.exists(filename):
            open(filename, 'w').close()
        
        return filename
        
    def config_load(self):
        filename = self.config_init()
        
        commands = open(filename).read().splitlines()
        self.ui.command.clear()
        self.ui.command.addItems(commands)
        self.ui.command.setCurrentIndex(-1)
        
    def command_save(self, command):
        filename = self.config_init()

        f = open(filename)
        lines = f.read().splitlines()[:50] # save last 100 commands
        f.close()

        if command in lines:
            lines.remove(command)
            
        lines.insert(0, command)

        f = open(filename, 'w')
        f.write('\n'.join(lines))
        f.close()

    def command_changed(self, command):
        self.ui.statusbar.clearMessage()
        
    def keyPressEvent(self, event):
        
        key = event.key()
        
        if event.modifiers() == QtCore.Qt.NoModifier and key == QtCore.Qt.Key_Escape:
            self.close()
            event.accept()
        
        elif (event.modifiers() == QtCore.Qt.KeypadModifier and key == QtCore.Qt.Key_Enter) or \
             (event.modifiers() == QtCore.Qt.NoModifier and key == QtCore.Qt.Key_Return):
            self.run()
            event.accept()
        
        if not event.isAccepted():
            super(MainForm, self).keyPressEvent(event)

    def run(self):
        command = unicode(self.ui.command.currentText()).strip()
        if command:
            try:
                res = subprocess.Popen(shlex.split(command), close_fds=False)
                ran = True
            except OSError as e:
                self.ui.statusbar.showMessage(u"Error %d: %s" % (e.errno, e.strerror.decode('utf-8')))
                ran = False
            
            if ran:
                self.command_save(command)
                self.close()

def main(argv=None):
    app = QtGui.QApplication(argv or sys.argv)
    app.setApplicationName("AltF2")

    dialer = MainForm(app)
    dialer.show()

    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main(sys.argv)

    
