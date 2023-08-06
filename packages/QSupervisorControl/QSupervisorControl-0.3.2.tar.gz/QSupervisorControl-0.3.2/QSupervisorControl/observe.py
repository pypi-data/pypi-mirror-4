# -*- coding: utf-8 -*-
from PyQt4 import QtCore
from QSupervisorControl import db
from QSupervisorControl.system import System

import time
import os
import re


class ObserverThread(QtCore.QThread):

    def __init__(self, program, msleep=1000, callback=None, *args, **kargs):
        super(ObserverThread, self).__init__(*args, **kargs)
        self.program = program
        session = db.get_session()
        try:
            launche = session.query(db.Launche).filter_by(
                name=program
            ).one()
        except:
            pass
        else:
            self.path = launche.path
            self.touch_file = launche.touch_file
            self.monitor_pattern = launche.monitor_pattern

        self.msleep = msleep
        self.callback = callback

        self.files = {}
        self.filter = re.compile(self.monitor_pattern)
        self.detect_changes(self.path)

    def do_touch(self):
        print('Release touch reload')
        if os.path.exists(self.touch_file):
            if os.path.isdir(self.touch_file):
                print('touch file is directory')
            elif os.path.isfile(self.touch_file):
                print('touched')
                os.utime(self.touch_file, None)
        else:
            fd = open(self.touch_file, 'w')
            fd.close()
            print('touch file created now')

    def detect_changes(self, path):
        changed = False
        for fname in [n for n in os.listdir(path) if n not in ('.', '..')]:
            fname = os.path.join(path, fname)
            if os.path.isdir(fname) is True:
                if self.detect_changes(fname) and changed is False:
                    changed = True
            elif self.filter.match(fname):
                st = os.stat(fname)
                if fname in self.files and self.files.get(fname) != st.st_mtime:
                    changed = True
                self.files.update({
                    fname: st.st_mtime
                })
        return changed

    def run(self):
        while True:
            if self.detect_changes(self.path):
                self.do_touch()
                self.callback is not None and self.callback.emit()
            time.sleep(self.msleep / 1000.0)
