from AccessControl import getSecurityManager

from transaction.interfaces import IDataManager

from zope.app.component.hooks import getSite
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from raptus.mercurialstorage import utils
from raptus.mercurialstorage.logger import getLogger

logger = getLogger(__name__)
def info(msg):
    if not msg:
        return
    logger.info(msg)

class MercurialDataManager(object):
    implements(IDataManager)
    
    def __init__(self, tm, path, message, userid):
        self.transaction_manager = tm
        self.path = path
        self.message = message
        self.userid = userid
        
    def abort(self, transaction):
        utils.system('hg revert --all -R %s' % self.path)
        
    def commit(self, transaction):
        portal = getSite()
        try:
            mship = getToolByName(portal, 'portal_membership')
            user = mship.getMemberById(self.userid)
            email = user.getProperty('email')
            name = user.getProperty('fullname')
        except:
            pass
        if not email:
            email = portal.getProperty('email_from_address', '')
            name = portal.getProperty('email_from_name', '')
        output = utils.system('hg commit --addremove -v -m "%s" -u "%s <%s>" -R %s' % (self.message, name, email, self.path))
        if output and not 'nothing changed' in output:
            info('\n'+output)

    def tpc_begin(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    tpc_abort = abort
        
    def sortKey(self):
        return 9999999999
    
    def __eq__(self, other):
        if hasattr(other, 'path'):
            return self.path == other.path
        return 0
    
    def __ne__(self, other):
        if hasattr(other, 'path'):
            return not self.path == other.path
        return 0