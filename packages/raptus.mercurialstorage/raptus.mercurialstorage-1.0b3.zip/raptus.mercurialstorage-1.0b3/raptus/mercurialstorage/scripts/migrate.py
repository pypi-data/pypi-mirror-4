"""
migrate -- migrate an existing site using raptus.mercurialstorage pre 1.0b3

Usage: bin/instance run path_to_this_script path_to_the_desired_plone_instance_in_zope [path_to_the_desired_plone_instance_in_zope] ..

Options:
-h/--help -- print usage message and exit

This script iterates over all objects in the given plone instances and
adjusts the stored paths of the fields using ExternalStorage. The stored
paths are made relative which is done by stripping the root path from
the beginning. The root path is provided by ExternalStorage and is either
the var directory in your zope instance home (when using buildout this is
located at: parts/instance/var) or if an environment variable named
EXTERNAL_STORAGE_BASE_PATH is set it's value is used instead. By temporarly
using this variable one may migrate the data of a moved buildout by setting
it to the old path.

"""
import sys, os
import transaction
from Testing.makerequest import makerequest
from zope.app.component import site
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ExternalStorage.ExternalStorage import ExternalStorage

try:
    from zope.traversing.interfaces import BeforeTraverseEvent
except ImportError: # plone < 4
    from zope.app.publication.interfaces import BeforeTraverseEvent

def setSiteManager(plone):
    ev = BeforeTraverseEvent(plone, plone.REQUEST)
    site.threadSiteSubscriber(plone, ev)

def migrate(path):
    print "starting migration of %s" % path
    try:
        parts = path.split('/')
        obj = app
        while len(parts):
            obj = obj._getOb(parts.pop(0))
        if not IPloneSiteRoot.providedBy(obj):
            print "  the object at %s is not a plone site" % path
            raise
        setSiteManager(obj)
        migrate_object(obj)
        print "finished migration of %s" % path
    except:
        print "migrating %s failed" % path
        return

def migrate_object(obj):
    try:
        transaction.begin()
        fields = obj.Schema().fields()
        for field in fields:
            if isinstance(field.getStorage(), ExternalStorage):
                migrate_field(field, obj)
        transaction.commit()
    except:
        transaction.abort()
        pass
    try:
        for child in obj.objectValues():
            migrate_object(child)
    except:
        pass

def migrate_field(field, obj):
    try:
        storage = field.getStorage()
        root = storage.getRootPath()
        if not root.endswith(os.path.sep):
            root += os.path.sep
        migrated = migrate_dict(obj._es, root)
        if migrated:
            print "  migrated field %s of %s" % (field.__name__, '/'.join(obj.getPhysicalPath()))
    except:
        pass

def migrate_dict(d, root):
    migrated = False
    for name, value in d.items():
        if isinstance(value, basestring) and name == 'filepath' and value.startswith(root):
            d[name] = value[len(root):]
            return True
        if hasattr(value, 'items'):
            migrated = migrated or migrate_dict(value, root)
    return migrated

def true_value(value, field, obj):
    return value and not value == field.getDefault(obj) and (not hasattr(value, 'get_size') or value.get_size() > 0)

print """
***********************************************************************************
                       raptus.mercurialstorage Migration


"""

app = makerequest(app)
args = sys.argv[1:]
while len(args):
    path = args.pop(0)
    if path == '-h' or path == '--help':
        print __doc__
        break
    migrate(path)

print """


***********************************************************************************
"""
