import os, sys, time, traceback, transaction
from threading import RLock
from Persistence import Persistent
from persistent.list import PersistentList

from AccessControl.SecurityManagement import setSecurityManager, getSecurityManager, newSecurityManager

from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from zope.interface import Interface, implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from raptus.mercurialstorage import storage_registry
from raptus.mercurialstorage.datamanager import MercurialDataManager
from raptus.mercurialstorage.logger import getLogger

logger = getLogger(__name__)
def info(msg):
    if not msg:
        return
    logger.info(msg)

QUEUE_KEY = 'raptus.mercurialstorage.queue'
QUEUE_LAZY_KEY = 'raptus.mercurialstorage.queue.lazy'

class IAction(Interface):
    """
    """
    
    def execute(app):
        """
        """
        
def _mark_asynch(obj):
    obj.asynch = True
        
def _unmark_asynch(obj):
    obj.asynch = False
        
class BaseAction(Persistent):
    _mark = True
    
    def __init__(self, context):
        Persistent.__init__(self)
        if self._mark:
            _mark_asynch(context)
            transaction.commit()
        portal_state = getMultiAdapter((context, context.REQUEST), name=u'plone_portal_state')
        self.userid = portal_state.member().getId()
        self.uid = context.UID()
    
    def pre_execute(self, plone):
        t = transaction.get()
        for storage in storage_registry:
            datamanger = MercurialDataManager(transaction.manager, storage.getRootPath(), str(self), self.userid)
            if not datamanger in t._resources:
                t.join(datamanger)
        ref = getToolByName(plone, 'reference_catalog')
        mship = getToolByName(plone, 'portal_membership')
        sm = getSecurityManager()
        try:
            user = mship.getMemberById(self.userid).getUser()
            newSecurityManager(plone.REQUEST, user)
        except:
            pass # no user found
        obj = ref.lookupObject(self.uid)
        if obj:
            _mark_asynch(obj)
        return obj, sm
        
    def post_execute(self, obj, sm):
        if obj:
            _unmark_asynch(obj)
            transaction.commit()
        setSecurityManager(sm)
        
    def __eq__(self, other):
        if isinstance(other, self.__class__) and \
           self.uid == other.uid and \
           self.userid == other.userid:
            return 1
        return 0

class SetAction(BaseAction):
    implements(IAction)
    
    def __init__(self, context, name, value, renaming, copying, **kwargs):
        BaseAction.__init__(self, context)
        self.name = name
        self.value = value
        self.renaming = renaming
        self.copying = copying
        if not getattr(self.value, 'filename', None) and context.REQUEST.form.get('%s_file' % name, None):
            self.value.filename = getattr(context.REQUEST.form.get('%s_file' % name), 'filename', None)
        self.mimetype = kwargs.get('mimetype', 'application/octet-stream')
        
    def execute(self, plone):
        obj, sm = self.pre_execute(plone)
        if obj:
            plone.REQUEST.form.update({'%s_file' % self.name: self.value})
            storage = obj.Schema().get(self.name).getStorage()
            r, c = getattr(obj, '_v_renaming', False), getattr(obj, '_v_copying', False)
            obj._v_renaming, obj._v_copying = self.renaming, self.copying
            storage.log(self.name, obj)
            storage._set(self.name, obj, self.value, **dict(mimetype=self.mimetype))
            obj._v_renaming, obj._v_copying = r, c
            obj.reindexObject()
        self.post_execute(obj, sm)
            
    def __str__(self):
        return '<SetAction uid="%s" name="%s" userid="%s" rename="%s" copy="%s">' % (self.uid, self.name, self.userid, self.copying, self.renaming)
        
    def __eq__(self, other):
        if super(SetAction, self).__eq__(other) and \
           self.name == other.name and \
           self.value == other.value and \
           self.renaming == other.renaming and \
           self.copying == other.copying:
            return 1
        return 0
        
class UnsetAction(BaseAction):
    implements(IAction)
    
    def __init__(self, context, path):
        BaseAction.__init__(self, context)
        self.path = path
    
    def execute(self, plone):
        obj, sm = self.pre_execute(plone)
        for storage in storage_registry:
            if self.path.startswith(storage.getRootPath()):
                storage._unset(self.path)
                break
        self.post_execute(obj, sm)
            
    def __str__(self):
        return '<UnsetAction path="%s">' % self.path
        
    def __eq__(self, other):
        if super(UnsetAction, self).__eq__(other) and \
           self.path == other.path:
            return 1
        return 0
        
class CleanupAction(BaseAction):
    implements(IAction)
    
    def __init__(self, context, path):
        BaseAction.__init__(self, context)
        self.path = path
        
    def execute(self, plone):
        obj, sm = self.pre_execute(plone)
        for storage in storage_registry:
            if self.path.startswith(storage.getRootPath()):
                storage._cleanupInstance(self.path)
                break
        self.post_execute(obj, sm)
            
    def __str__(self):
        return '<CleanupAction path="%s">' % self.path
        
    def __eq__(self, other):
        if super(CleanupAction, self).__eq__(other) and \
           self.path == other.path:
            return 1
        return 0

processor_lock = RLock()
processor_lazy_lock = RLock()

class Processor(BrowserView):
    
    def __call__(self):
        if not processor_lock.acquire(False):
            return
        try:
            annotations = IAnnotations(self.context)
            processor_lazy_lock.acquire()
            try:
                if not annotations.has_key(QUEUE_KEY):
                    annotations[QUEUE_KEY] = PersistentList()
                queue = annotations[QUEUE_KEY]
                if annotations.has_key(QUEUE_LAZY_KEY):
                    queue_lazy = annotations[QUEUE_LAZY_KEY]
                    while len(queue_lazy):
                        queue.append(queue_lazy.pop(0))
            finally:
                processor_lazy_lock.release()
            if not annotations.has_key(QUEUE_KEY):
                return
            queue = annotations[QUEUE_KEY]
            previous = None
            while len(queue):
                sp = transaction.savepoint(optimistic=True)
                action = queue.pop(0)
                if action == previous:
                    info('skipping action %s' % action)
                    continue
                info('starting action %s' % action)
                try:
                    action.execute(self.context)
                    previous = action
                    info('action finished %s' % action)
                except Exception, e:
                    sp.rollback()
                    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                    info('action failed %s\n%s' % (action, ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback))))
                    break
        finally:
            processor_lock.release()

class ActionHook(object):
    
    def __init__(self, action):
        self.action = action
        
    def __call__(self, committed):
        if committed:
            processor_lazy_lock.acquire()
            try:
                plone = getSite()
                key = QUEUE_LAZY_KEY
                annotations = IAnnotations(plone)
                if not annotations.has_key(key):
                    annotations[key] = PersistentList()
                if len(annotations[key]) and \
                   self.action == annotations[key][-1]:
                    info('skipping action %s' % self.action)
                else:
                    annotations[key].append(self.action)
                    transaction.commit()
                    info('appended action %s' % self.action)
            finally:
                processor_lazy_lock.release()

def append(action):
    transaction.get().addAfterCommitHook(ActionHook(action))