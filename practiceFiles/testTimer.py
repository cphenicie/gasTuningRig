import sys
import time

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

def tick():
    print 'tick'

timer = QTimer()
timer.timeout.connect(tick)
timer.start(1000)


# run event loop so python doesn't exit
# app.exec_()
while 1:
    curr = time.time() * 1000
    wait = 1000
    while 1:
        if time.time()*1000 > curr+wait:
            print('asdfasdf')
            break
