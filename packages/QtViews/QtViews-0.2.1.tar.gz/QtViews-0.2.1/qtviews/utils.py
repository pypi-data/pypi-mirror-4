from PySide import QtCore, QtGui

_test_app = None

def qtapp():
    """
    A QApplication creator for test cases.  QApplication is a single-ton and 
    this provides a safe construction wrapper.
    
    >>> app=qtapp()
    >>> # put test code here
    """
    global _test_app
    _test_app = QtGui.QApplication.instance()
    if _test_app is None:
        _test_app = QtGui.QApplication([])
    return _test_app
