# -*- coding: utf-8 -*-
'''
Copyright 2012 Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from PyQt4 import QtGui
from PyQt4 import QtCore
from supervisor import supervisorctl
from QSupervisorControl.ui.about import AboutDialog
from QSupervisorControl.ui.configuration import ConfigurationDialog
from QSupervisorControl.ui.logview import LogViewDialog
from QSupervisorControl.system import *
from QSupervisorControl.observe import ObserverThread

import os
import sys
import re
import gettext
import db

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

app_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(app_dir, 'data')

gettext.bindtextdomain('base', os.path.join(data_dir, 'i18n'))
gettext.textdomain('base')
_ = gettext.gettext


def proxy_func(func, *args, **kargs):
    def wrapper():
        func(*args, **kargs)
    return wrapper


class StatusObserve(QtCore.QThread):

    def __init__(self, controller):
        QtCore.QThread.__init__(self)
        self._controller = controller

    def run(self):
        while True:
            self._controller.emit(QtCore.SIGNAL('observe'))
            self.sleep(1)


class SupervisorController(QtGui.QSystemTrayIcon):

    PARSE_STATUS = re.compile(r'^(?P<name>(\w|-|\d)+)\s+(?P<status>\w+).*$')

    def _void(self):
        pass

    def get_programs(self):
        swap = sys.stdout
        out = StringIO()
        sys.stdout = out
        supervisorctl.main(('status',))
        sys.stdout = swap

        flag = False
        for line in out.getvalue().split('\n'):
            rst = self.PARSE_STATUS.match(line.replace('\n', ''))
            if rst is not None:
                flag = True
                print rst.groupdict()
                yield rst.groupdict()

        if flag is False:
            print _('Foi detectado um problema ao acessar o supervisorctl')
            print _('Verifique se seu usuário tem direito de acesso.')

            return

    def get_status(self, program):
        swap = sys.stdout
        out = StringIO()
        sys.stdout = out
        supervisorctl.main(('status', program))
        sys.stdout = swap

        rst = self.PARSE_STATUS.match(out.getvalue().replace('\n', '\0'))

        if rst is not None:
            return rst.groupdict().get('status')
        else:
            return None

    def _exit(self):
        self._app.quit()

    def do(self, program='all', action=None):
        supervisorctl.main((action, program))

    def register_to_observe(self, program, menu, action):
        if hasattr(self, '_to_observe') is False:
            self._to_observe = {}
        if program not in self._to_observe.keys():
            self._to_observe.update({
                program: {
                    'menu': menu,
                    'action': action
                }
            })

            session = db.get_session()
            if session.query(db.Launche).filter(db.Launche.name == program).count() == 0:
                session.add(db.Launche(name=program))
                session.commit()

    def changeActionIcon(self, action, icon):
        action.setIcon(QtGui.QIcon(os.path.join(data_dir, '%s.png' % icon.lower())))

    observe = QtCore.pyqtSignal()

    def _observe(self):
        translate = {
            'STOPPED': _('Parado'),
            'RUNNING': _('Rodando'),
            'FATAL': _('Falhou')
        }

        if hasattr(self, '_to_observe'):
            for program, info in self._to_observe.items():
                status = self.get_status(program)
                if status is not None:
                    info.get('action').setText(translate.get(status, _('Desconhecido')))
                    self.changeActionIcon(info.get('menu'), status)
                else:
                    print program
        else:
            self._createContextMenu()

    def recreateContextMenu(self):
        self.setContextMenu(self._createContextMenu())

    def config_monitor(self, program):
        dialog = ConfigurationDialog(program, System.wnd)
        dialog.load_data()
        dialog.show()

    def start_monitor(self, program):
        conf = getattr(self, '_start_monitor', {})
        if program in conf:
            conf.get(program).quit()
            conf.remove(program)
        else:
            t = ObserverThread(
                program,
                callback=self.touch_detect,
                parent=self
            )
            t.start()
            conf.update({program: t})

    touch_detect = QtCore.pyqtSignal()

    def _touch_detect(self):
        pass

    def show_logview(self, program):
        dialog = LogViewDialog(program, System.wnd)
        dialog.show()

    def _createContextMenu(self):
        menu = QtGui.QMenu()
        menu.addAction(_('Iniciar todos'), proxy_func(self.do, **{'action': 'start'}))
        menu.addAction(_('Parar todos'), proxy_func(self.do, **{'action': 'stop'}))
        menu.addAction(_('Reiniciar todos'), proxy_func(self.do, **{'action': 'restart'}))

        menu.addSeparator()
        for program in self.get_programs():
            sub_menu = menu.addMenu(program.get('name').capitalize())
            self.register_to_observe(
                program.get('name'),
                sub_menu,
                sub_menu.addAction(program.get('status')),
            )

            sub_menu.addSeparator()
            sub_menu.addAction(_('Iniciar'), proxy_func(self.do, **{'program': program.get('name'), 'action': 'start'}))
            sub_menu.addAction(_('Parar'), proxy_func(self.do, **{'program': program.get('name'), 'action': 'stop'}))
            sub_menu.addAction(_('Reiniciar'), proxy_func(self.do, **{'program': program.get('name'), 'action': 'restart'}))
            sub_menu.addSeparator()
            sub_menu.addAction(
                _('Configurar'),
                proxy_func(
                    self.config_monitor, **{
                    'program': program.get('name')
                })
            )
            sub_menu.addSeparator()
            act = sub_menu.addAction(
                _(u'Monitorar mudanças'),
                proxy_func(
                    self.start_monitor,
                    **{
                        'program': program.get('name')
                    }
                )
            )
            act.setCheckable(True)
            act.setChecked(False)

            sub_menu.addAction(
                _(u'Visualizar logs'),
                proxy_func(
                    self.show_logview,
                    **{
                        'program': program.get('name')
                    }
                )
            )


        menu.addSeparator()
        menu.addAction(_(u'Sobre'), self.about_show)

        menu.addSeparator()
        menu.addAction(_('&Finalizar') + (' ' * 50), self._app.quit)

        return menu

    def about_show(self):
        about = AboutDialog(System.wnd)
        about.show()

    def __init__(self, app):
        QtGui.QSystemTrayIcon.__init__(
            self,
            QtGui.QIcon(os.path.join(data_dir, 'icon.png')),
            app
        )

        QtCore.QObject.connect(self, QtCore.SIGNAL('observe'), self._observe)
        # self.observe.connect(self._observe)
        self.touch_detect.connect(self._touch_detect)

        self._app = app
        self.setContextMenu(self._createContextMenu())
        self._thread = StatusObserve(self)
        self._thread.start()

