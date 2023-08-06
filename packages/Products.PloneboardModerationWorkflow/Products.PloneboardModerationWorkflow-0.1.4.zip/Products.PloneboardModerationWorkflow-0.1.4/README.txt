What is this?
=============

This Plone product gives you a new set of `Ploneboard`__ workflows. The idea is to update the basic
workflows to use also new Plone 3 style roles.

__ http://pypi.python.org/pypi/Products.Ploneboard

**Be aware**. Yes, we overwrite the basic Ploneaboad workflows, so you don't need to perform additional
operation (just "Manage Security Setting" inside ZMI).

Also some basic Ploneboard security settings has been changed. Forum inside private folders *are no more
accessible*. No more "Anonymous" explicit view permissions!

Roles
-----

Keeping *Member*, *Manager* and *Reviewer* role settings, the new workflows set add special permissions
also to *Reader* and *Contributor* roles.

Here a general explanation:

  `Reader`
      A Reader can access forum and discussions normally. The only difference from a Reader and a normal
      user is inside *private* boards (or when boards are put inside private folders).
      A Reader can't see not-published comments.
  `Contributor`
      A Contributor can write inside a forum. Basic Ploneboard workflows manage only the Member or Owner
      role, so is not simple to make groups of users that can write inside forums and other not.
      In general, Contributors can write inside boards and forum not accessible to all members of the
      site.

TODO
====

Need tests!

Credits
=======

Developed with the support of `Azienda USL Ferrara`__; Azienda USL Ferrara supports the
`PloneGov initiative`__.

.. image:: http://www.ausl.fe.it/logo_ausl.gif
   :alt: Azienda USL's logo

__ http://www.ausl.fe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

