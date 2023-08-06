from __future__ import absolute_import

from ..vtask import VTask

import glib


class GlibMainLoopTask(VTask):
    mainloop = None

    def initTask(self):
        super(GlibMainLoopTask, self).initTask()
        glib.threads_init()
        self.mainloop = glib.MainLoop()

    def _runloop(self):
        self.mainloop.run()

    def stop(self):
        if self.mainloop is None:
            return

        super(GlibMainLoopTask, self).stop()
        self.mainloop.quit()
        self.mainloop = None
