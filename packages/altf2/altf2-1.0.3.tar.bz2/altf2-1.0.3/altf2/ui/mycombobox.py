
from PyQt4 import QtCore, QtGui

class MyComboBox(QtGui.QComboBox):
    
    def keyPressEvent(self, event):
        
        key = event.key()
        event.setAccepted(False)
        
        if event.modifiers() == QtCore.Qt.NoModifier and key == QtCore.Qt.Key_Escape:
            self.parent().parent().close()
            event.accept()
        
        elif (event.modifiers() == QtCore.Qt.KeypadModifier and key == QtCore.Qt.Key_Enter) or \
             (event.modifiers() == QtCore.Qt.NoModifier and key == QtCore.Qt.Key_Return):
            self.parent().parent().run()
            event.accept()

        if not event.isAccepted():
            super(MyComboBox, self).keyPressEvent(event)

