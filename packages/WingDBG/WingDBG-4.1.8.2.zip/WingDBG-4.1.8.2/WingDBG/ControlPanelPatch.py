
import WingDBG
from App.ApplicationManager import ApplicationManager

if hasattr(ApplicationManager, 'old_objectItems'):
    ApplicationManager.old_beforeWing_objectItems = ApplicationManager.old_objectItems
ApplicationManager.old_objectItems = ApplicationManager.objectItems

def wingObjectItems(self, spec=None):
    if WingDBG.WingDebugService.id not in self.objectIds():
        wdbgs = WingDBG.WingDebugService()
        self._setObject(wdbgs.id, wdbgs)
        #self._objects = cp._objects+({'id': wdbgs.id,
        #                            'meta_type': wdbgs.meta_type},)

        return self.old_objectItems()

ApplicationManager.objectItems = wingObjectItems
