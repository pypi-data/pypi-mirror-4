Introduction
============

raptus.mercurialstorage depends on Products.ExternalStorage 0.7 which has some flaws and
needs to be patched in order to work correctly. The patch may be applied by using the
following part in your buildout:

::

    [patch_es_storage]
    recipe = iw.recipe.cmd:py
    on_install = true
    on_update = true
    cmds =
        >>> import os
        >>> patch = os.path.join("""${buildout:directory}""".strip(), 'eggs/raptus.mercurialstorage-0.4-py2.4.egg/raptus/mercurialstorage', 'es.patch')
        >>> file = os.path.join("""${buildout:directory}""".strip(), 'eggs/Products.ExternalStorage-0.7-py2.4.egg/Products/ExternalStorage/ExternalStorage.py')
        >>> if os.path.exists(file):
        >>>     os.system('patch -N %s %s' % (file, patch))

You also need mercurial working copies at the root of your storages so if you have a field
on which you use an ExternalMercurialStorage with a prefix of foo make sure a folder with
the name foo exists in your instances var folder and is initialized using 'hg init'. If
you are using buildout, there are two var folders, one in your buildout's root and one
at parts > instance, the aforementioned folder has to be created in the latter one.

All the mercurial commits are handled asynchronous using a queue, as a side effect the
files saved to mercurial storage are not immediately visible in plone, in this case a
attribute called 'asynch' is set on the content instance, which may be used to display
an information message to the user. The mentioned queue is processed by a view named
'processMercurialActionQueue' which has to be called regularly by a user having the
'Manage portal' permission. It is suggested to use zope clock server to call this view
about ever minute or more, add the following configuration to your instance part's
zope-conf-additional variable:

::

    <clock-server>
      method [PATH_TO_YOUR_PLONE_SITE]@@processMercurialActionQueue
      period 60
      user [MANAGER_USERID]
      password [MANAGER_PWD]
      host localhost
    </clock-server>

raptus.mercurialstorage logs to a different log file which is found in your log folder
under the name mercurial.log.


Migration from pre 1.0b3
========================

Products.ExternalStorage stores absolute file paths in the ZODB which makes moving existing
plone instances a pain. This issue was fixed in version 1.0b3 of raptus.mercurialstorage.
To migrate an existing plone site use the migrate script located in the scripts folder of the
raptus.mercurialstorage egg. Information about the usage of the script are given by executing:

::

    bin/instance run path_to_the_script -h

