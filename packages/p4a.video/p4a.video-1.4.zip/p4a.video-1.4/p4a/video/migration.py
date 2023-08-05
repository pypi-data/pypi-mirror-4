from zope import interface
from zope import component
from Products.CMFCore import utils as cmfutils
from OFS import interfaces as ofsifaces

class IMigratable(interface.Interface):
    def migrate():
        """Migrate the contextual object.
        """

class IMigrator(interface.Interface):
    def migrate(container, provides):
        """Search out all objects in a container and migrate them if
        possible.  The *provides* argument specifies the necessary
        interface an object must provide to even attempt migration.  This
        method should return the total number of objects migrated.
        """

class Migrator(object):
    interface.implements(IMigrator)
    
    def _attempt(self, container, obj):
        migratable = component.queryMultiAdapter((container, obj), 
                                                 IMigratable)
        if migratable is not None:
            if migratable.migrate():
                self.migrated += 1

    def _walk(self, objmanager, provides):
        for obj in objmanager.objectValues():
            if provides.providedBy(obj):
                self._attempt(objmanager, obj)
            childobjmanager = ofsifaces.IObjectManager(obj, None)
            if childobjmanager is not None:
                self._walk(childobjmanager, provides)

    def migrate(self, container, provides):
        self.migrated = 0
        objmanager = ofsifaces.IObjectManager(container)
        self._walk(objmanager, provides)
        return self.migrated
