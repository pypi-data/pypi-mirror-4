import os

from Acquisition import aq_parent

from persistent.dict import PersistentDict

from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.SecurityManagement import getSecurityManager, newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser

from OFS.Image import File

from zope.interface import alsoProvides
from zope.annotation import IAnnotations

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.ExternalStorage.ExternalStorage import ExternalStorage
from Products.ExternalStorage.filewrapper import FileWrapper

from Products.Archetypes.interfaces.field import IObjectField

from raptus.mercurialstorage import storage_registry, utils
from raptus.mercurialstorage.queue import append, SetAction, UnsetAction, CleanupAction

LOG_KEY = 'raptus.mercurialstorage.LOG'

class NamedUnrestrictedUser(UnrestrictedUser):
    def getId(self):
        return self.id

manager = NamedUnrestrictedUser('System Processes','',('Manager',), [])

class ExternalMercurialStorage(ExternalStorage):
    """
    """

    security = ClassSecurityInfo()
    
    def __init__(self, prefix='files', archive=False, rename=False, suffix='',
                 path_method='getExternalPath'):
        """Initializes default values.
        """
        ExternalStorage.__init__(self, prefix, archive, rename, suffix, path_method)
        storage_registry.append(self)

    security.declarePrivate('initializeInstance')
    def initializeInstance(self, instance, item=None, container=None):
        """
        """
        path = '/'.join(instance.getPhysicalPath())
        rename_or_copy = False
        if self.isInitialized(instance) and \
           self.getInstancePath(instance) != path:
            rename_or_copy = True
            instance._v_renaming = True
            if not self.hasTempData(instance):
                instance._v_copying = True
        if rename_or_copy:
            try:
                sm = getSecurityManager()
                manager.id = sm.getUser().getId()
                newSecurityManager(instance.REQUEST, manager)
                ExternalStorage.initializeInstance(self, instance, item, container)
                setSecurityManager(sm)
            except Unauthorized:
                pass
        else:
            ExternalStorage.initializeInstance(self, instance, item, container)
        instance._v_renaming, instance._v_copying = False, False

    security.declarePrivate('cleanupInstance')
    def cleanupInstance(self, instance, item=None, container=None):
        """Remove filesystem structure.
        """
        if instance.isTemporary():
            return
        pu = getToolByName(instance, 'portal_url')
        relative = pu.getRelativeContentPath(instance)
        path = os.path.join(self.getRootPath(), '/'.join(relative))
        append(CleanupAction(instance, path))

    security.declarePrivate('cleanupInstance')
    def _cleanupInstance(self, path):
        """Remove filesystem structure.
        """
        abs_path = os.path.join(self.getRootPath(), path)
        while path:
            # remove dir if empty
            if os.path.exists(path) and len(os.listdir(path)) == 0:
                os.rmdir(path)
            else:
                break
            path = os.path.dirname(path)

    security.declarePrivate('cleanupField')
    def cleanupField(self, instance, field, **kwargs):
        """
        """
        name = field.getName()
        self.unset(name, instance, **kwargs)
        
    security.declarePrivate('set')
    def set(self, name, instance, value, **kwargs):
        """
        """
        if value and hasattr(value, 'get_size') and value.get_size() and not instance.isTemporary():
            append(SetAction(instance, name, value, getattr(instance, '_v_renaming', False), getattr(instance, '_v_copying', False), **kwargs))
        else:
            self._set(name, instance, value, **kwargs)

    security.declarePrivate('_set')
    def _set(self, name, instance, value, **kwargs):
        """
        """
        ExternalStorage.set(self, name, instance, value, **kwargs)

    security.declarePrivate('setStorageItem')
    def setStorageItem(self, instance, name, value):
        """Sets an item into ES storage area.
        """
        if instance.isTemporary():
            return
        # check for old item to perform a move/copy
        filepath = os.path.join(self.getRootPath(), value.get('filepath'))
        old_item = self.getStorageItem(instance, name)
        if old_item:
            old_filepath = os.path.join(self.getRootPath(), old_item.get('filepath'))
            if not old_filepath == filepath and os.path.exists(old_filepath):
                if not getattr(instance, '_v_copying', False):
                    os.remove(old_filepath)
                    ExternalStorage.setStorageItem(self, instance, name, value)
                    self.recursiveDelete(os.path.dirname(old_filepath))
                    return
        ExternalStorage.setStorageItem(self, instance, name, value)

    security.declarePrivate('log')
    def log(self, name, instance):
        """
        """
        if instance.isTemporary():
            return
        annotations = IAnnotations(instance)
        if not annotations.has_key(LOG_KEY):
            annotations[LOG_KEY] = PersistentDict()
        if not annotations[LOG_KEY].has_key(name):
            annotations[LOG_KEY][name] = PersistentDict()
        revision = self.getRevision(instance, name)
        if not revision:
            return
        try:
            data = PersistentDict()
            data['filepath'] = self.getFilepath(instance, name)
            data['filename'] = self.getFilename(instance, name)
            data['mimetype'] = self.getContentType(instance, name)
            annotations[LOG_KEY][name][revision] = data
        except AttributeError:
            pass

    security.declarePrivate('unset')
    def unset(self, name, instance, **kwargs):
        self.log(name, instance)
        try:
            ExternalStorage.unset(self, name, instance, **kwargs)
        except Unauthorized:
            sm = getSecurityManager()
            manager.id = sm.getUser().getId()
            newSecurityManager(instance.REQUEST, manager)
            ExternalStorage.unset(self, name, instance, **kwargs)
            setSecurityManager(sm)
            pass
        if instance.isTemporary():
            return
        append(UnsetAction(instance, os.path.join(self.getRootPath(), self.getFilepath(instance, name))))

    security.declarePrivate('_unset')
    def _unset(self, path, **kwargs):
        """
        """
        if path.endswith('/image') and os.path.exists(path[:-6]):
            path = path[:-6]
        instance_path = os.path.dirname(path)
        if os.path.exists(path):
            os.remove(path)
        self._cleanupInstance(instance_path)

    security.declarePrivate('getFileSystemPath')
    def getFileSystemPath(self, instance, item):
        """Returns the file system path (with filename) where to store
        a instance field.
        """
        path = ExternalStorage.getFileSystemPath(self, instance, item)
        # try to find an appropriate extension
        try:
            basename, extension = os.path.splitext(getattr(instance.REQUEST.form.get('%s_file' % item), 'filename', self.getStorageItem(instance, item).get('filepath')))
            path = '%s%s' % (path, extension)
        except:
            pass
        return path
    
    def getRevision(self, instance, name):
        return utils.system('hg tip -R %s --template "{node}"' % self.getRootPath())
        
    security.declarePrivate('getByRevision')
    def getByRevision(self, instance, name, rev):
        """
        """
        info = dict(self.getInfoByRevision(instance, name, rev))
        filename = info['filename']
        filepath = os.path.join(self.getRootPath(), info['filepath'])
        if filename:
            filepath = os.path.join(filepath, filename)
        return utils.system('hg cat -R %s -r %s %s' % (self.getRootPath(), rev, filepath))
        
    security.declarePrivate('getInfoByRevision')
    def getInfoByRevision(self, instance, name, rev):
        """ Get info about a storage item by a give revision
        """
        annotations = IAnnotations(instance)
        if not annotations.has_key(LOG_KEY) or \
           not annotations[LOG_KEY].has_key(name) or \
           not annotations[LOG_KEY][name].has_key(rev):
            return
        return annotations[LOG_KEY][name][rev]
    
    def recursiveDelete(self, path):
        while not os.path.exists(path) or not os.path.isdir(path):
            path = os.path.dirname(path)
        if len(os.listdir(path)) > 0:
            return
        if not path == self.getRootPath():
            os.rmdir(path)
            self.recursiveDelete(os.path.dirname(path))
        