QDarkStylesheet
==================

A dark stylesheet for Qt applications.


License
---------

This project is licensed under the LGPL v3


Installation
---------------

If you are using python, all you have to do is to run setup script or to install it from pypi:

```bash
pip install qdarkstyle
```

or

```bash
python setup.py install
```

If you are using C++, the best way is to download/clone the project and copy
the following files to your application directory:
    - qdarkstyle/style.qss
    - qdarkstyle/style.qrc
    - qdarkstyle/rc (the whole directory)

Usage
-------------

Here is an example using PySide:


```Python
import sys
import qdarkstyle
from PySide import QtGui


# create the application and the main window
app = QtGui.QApplication(sys.argv)
window = QtGui.QMainWindow()

# setup stylesheet
app.setStyleSheet(qdarkstyle.load_stylesheet())

# run
window.show()
app.exec_()
```


_There is an example included in the example folder. You can run the script without installing qdarkstyle. You
only need to have PySide installed on your system._

Status:
-------------

The following widgets are styled: 

 - QMainWindow
 - QWidget
 - QMenu, QMenuBar
 - QToolTip
 - QAbstractItemView
 - QLineEdit
 - QGroupBox
 - QTextEdit, QPlainTextEdit
 - QTreeView,
 - QScrollBar
 - QRadioButton
 - QCheckBox
 - QComboBox
 - QPushButton
 - QToolButton
 - QToolBar
 - QProgressBar
 - QSpinBox
 - QFrame
 - QTabWidget, QTabBar
 - QDockWidget
 - QSlider (horizontal and vertical)

What still needs to be done:

 - QAbstractScrollArea
 - QSplitter
 - QStatusBar
 - QToolBox 


Contact information:
--------------------------

  - Maintainer: colin.duquesnoy@gmail.com
  - Homepage: https://github.com/ColinDuquesnoy/QDarkStyleSheet


Snapshots
-------------

I have used this stylesheet for an internal tool at work. Are are a few screenshots:

![alt text](/screenshots/01.png "Screenshot 01")
