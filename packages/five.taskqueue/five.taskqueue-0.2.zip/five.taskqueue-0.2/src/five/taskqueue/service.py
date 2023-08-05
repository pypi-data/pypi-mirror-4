
from BTrees.IOBTree import IOBTree
from OFS.SimpleItem import SimpleItem

try:
    from BTrees import family32
    MAXINT = family32.maxint
except ImportError:
    import sys
    MAXINT = sys.maxint

from z3c.taskqueue.baseservice import BaseTaskService
from five.taskqueue import processor


class TaskService(BaseTaskService, SimpleItem):
    containerClass = IOBTree
    maxint = MAXINT

    processorFactory = processor.SimpleProcessor

    def getServicePath(self):
        path = [part for part in self.getPhysicalPath() if part]
        return path


def setNameAndParent(object, event):
    object.__name__ = event.newName
    event.object.__parent__ = event.newParent
