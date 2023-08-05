isotoma.recipe.ploneprefetch
============================

This recipe prefetches all the Plone eggs contained in a unified installer.
This vastly reduces the number of eggs that have to be installed giving Travis
a chance of actually building your code before hitting a timeout.

Just do::

    [prefetch]
    recipe = isotoma.recipe.ploneprefetch
    url = http://launchpad.net/plone/4.1/4.1/+download/Plone-4.1-UnifiedInstaller-20110907.tgz
    python = 2.6

The python version is just to stop a python 2.6 user from downloading the
unified installer for plone 4.2 which is 2.7 only. It's optional.

