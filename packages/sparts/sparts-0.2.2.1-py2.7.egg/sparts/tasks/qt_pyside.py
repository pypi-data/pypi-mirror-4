from ..vtask import VTask
from pyside.QtCore import QCoreApplication, Slot
from pyside.QtGui import QApplication

class QCoreApplicationTask(VTask):
    APP_CLASS = QCoreApplication

    def _makeApplication(self):
        return self.APP_CLASS(self.service.options)

    def initTask(self):
        super(QCoreApplicationTask, self).initTask()
        self.application = self._makeApplication(self)

    def stop(self):
        super(QCoreApplicationTask, self).stop()
        self.application.exit()

    def _runloop(self):
        self.application.aboutToQuit.connect(self._handle_shutdown)
        self.application.exec_()

    @Slot
    def _handle_shutdown(self):
        self.service.shutdown()


class QApplicationTask(QCoreApplicationTask):
    APP_CLASS = QApplication
