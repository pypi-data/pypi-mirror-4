Introduction
============

Since Plone 4.0 you can configure Plone to allow users to login with
their email address, using a setting in the Security control panel.
This works fine out of the box.  Some improvements would be useful
though that need some more careful consideration before being added to
core Plone.  That is where this package comes in.

This is a temporary package with some fixes for when you want to use
the email address of a user as login name in Plone 4.  It also
introduces a few hooks for determining the user id and login name of a
new user.


Plone version
-------------

This package is tested with Plone 4.1, 4.2 and 4.3.  It will not work
in 4.0.

For Plone 3, you must use the ``collective.emaillogin`` package.


Dependencies
------------

We need a newer version of ``Products.PluggableAuthService`` than is
available currently in the latest Plone versions.  Assuming you are
using buildout for your Plone site, you need to add a line to a
versions section::

  Products.PluggableAuthService = 1.10.0

Any version newer than this is fine as well.  If your Plone version
already has this version or a newer one pinned, then you do not need
to add this line.

Note that at the time of writing this version was not yet available on
PyPI.  It is expected soon, so `check there`_ what the latest version is.

.. _`check there`: http://pypi.python.org/pypi/Products.PluggableAuthService


What does this package do?
--------------------------

Clearer separation between user id and login name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The validation of the ``register`` browser view uses two methods to
get a user id and login name::

    # Generate a nice user id and store that in the data.
    user_id = self.generate_user_id(data)
    # Generate a nice login name and store that in the data.
    login_name = self.generate_login_name(data)

After this, the ``data`` dictionary will have keys ``user_id`` and
``login_name`` set accordingly.

We avoid as much as possible the use of ``username`` as a variable,
because no one ever knows if that is meant as a user id or as a login
name.  In standard Plone this is always the same, but this need not be
true, especially when using the email address as login name.

These changes are intended to be merged to ``plone.app.users``.


Control over user ids
~~~~~~~~~~~~~~~~~~~~~

An ``IUserIdGenerator`` interface is defined.  This is used in the new
``generate_user_id`` method of the ``register`` browser view (also
used when adding a new user as admin).  Two sample implementations::

  def uuid_userid_generator(data=None):
      # Return a uuid, independent of the data.
      # This is available in utils.py in the plone.app.users patches.
      from zope.component import getUtility
      from plone.uuid.interfaces import IUUIDGenerator
      generator = getUtility(IUUIDGenerator)
      return generator()

  def login_name_as_userid_generator(data):
      # We like to keep it simple.
      return data.get('username')

In ``generate_user_id`` we try a few options for coming up with a good
user id:

1. We query a utility, so integrators can register a hook to
   generate a user id using their own logic::

     generator = queryUtility(IUserIdGenerator)
     if generator:
         userid = generator(data)
         if userid:
             data['user_id'] = userid
             return userid

2. If ``use_uuid_as_userid`` is set in the site_properties, we
   generate a uuid.  This is a new property introduced by this
   package and can be set in the Security control panel.

3. If a username is given and we do not use email as login,
   then we simply return that username as the user id.

4. We create a user id based on the full name, if that is
   passed.  This may result in an id like ``bob-jones-2``.

When the email address is used as login name, we originally
used the email address as user id as well.  This has a few
possible downsides, which are the main reasons for the new,
pluggable approach:

- It does not work for some valid email addresses.

- Exposing the email address in this way may not be wanted.

- When the user later changes his email address, the user id
  will still be his old address.  It works, but may be
  confusing.

Another possibility would be to simply generate a uuid, but that is
ugly.  We could certainly try that though: the big plus here would be
that you then cannot create a new user with the same user id as a
previously existing user if this ever gets removed.  If you would get
the same id, this new user would get the same global and local roles,
if those have not been cleaned up.

When a user id is chosen, the ``user_id`` key of the data gets
set and the user id is returned.

These changes are intended to be merged to ``plone.app.users``.


Control over login names
~~~~~~~~~~~~~~~~~~~~~~~~

Similarly, an ``ILoginNameGenerator`` interface is defined.

Usually the login name and user id are the same, but this is
not necessarily true.  When using the email address as login
name, we may have a different user id, generated by calling
the generate_user_id method.

We try a few options for coming up with a good login name:

1. We query a utility, so integrators can register a hook to
   generate a login name using their own logic::

     pas = getToolByName(self.context, 'acl_users')
     generator = queryUtility(ILoginNameGenerator)
     if generator:
         login_name = generator(data)
         if login_name:
             login_name = pas.applyTransform(login_name)
             data['login_name'] = login_name
           return login_name

2. If a username is given and we do not use email as login,
   then we simply return that username as the login name.

3. When using email as login, we use the email address.

In all cases, we call PAS.applyTransform on the login name, if
that is defined.  This is a recent addition to PAS, currently
under development.

When a login name is chosen, the ``login_name`` key of the data gets
set and the login name is returned.

These changes are intended to be merged to ``plone.app.users``.


Lowercase login names
~~~~~~~~~~~~~~~~~~~~~

We store login names as lowercase.  The email addresses themselves can
actually be mixed case, though that is not really by design, more a
(happy) circumstance.

This needs branch ``maurits-login-transform`` of
``Products.PluggableAuthService``.  That branch introduces a property
``login_transform``.  Setting this to ``lower`` the ``lower`` method
of PAS is called whenever a login name is given.

All relevant places in ``plone.app.users`` have been changed to take
this new property into account, using code like this::

  login_name = pas.loginTransform(login_name)

In the security panel of ``plone.app.controlpanel`` we change the
``set_use_email_as_login`` method to set ``login_transform`` to lower
case when switching on email as login name.  For safety, we never
change this back to the default empty string.  This is fine for normal
non-email login names as well.

Note that when ``login_transform`` is ``lower``, the end user can
login with upper case ``JOE`` and he will then be logged in with login
name ``joe``, as long as the password is correct of course.  If you
somehow still have an upper or mixed case login name, you cannot
login.

Setting the login_transform to a non empty string will
automatically apply this transform to all existing logins in your
database.

Note: when this is merged to core Plone, login names will not be
transformed to lowercase by default.  The option will simply be
available if the site admin wants it.  Switching on email as login
will also switch on lowercase login names.


Updating login names
--------------------

We have a patch for the ``ZODBMutablePropertyProvider`` of
``Products.PlonePAS`` that adds two new but empty methods required by
the changed ``IUserEnumerationPlugin`` interface of PAS::

  def updateUser(self, user_id, login_name):
     pass


  def updateEveryLoginName(self, quit_on_first_error=True):
     pass

This has been merged to ``Products.PlonePAS``.


Control panels
~~~~~~~~~~~~~~

Switching email as login name on or off in the security panel now
automatically updates existing login names.  It may fail when there
are duplicates.

The updating of existing users used to be done in the
``@@migrate-to-emaillogin`` view (class ``EmailView``) from
``plone.app.controlpanel``.  We have simplified this page to only
search for duplicate login names.  You can search for duplicate email
addresses or duplicate user ids, always lower case.

The security panel now has an option ``Use UUID user ids``, by default
switched off.


Set own login name
~~~~~~~~~~~~~~~~~~

The ``Products.CMFPlone.utils.set_own_login_name`` method is
drastically simplified, with the former code being moved to PAS
itself::

  def set_own_login_name(member, loginname):
      """Allow the user to set his/her own login name.
      """
      pas = getToolByName(member, 'acl_users')
      pas.updateOwnLoginName(loginname)


Installation
~~~~~~~~~~~~

When installing this add-on in the Add-ons control panel, the
following is done.

- It adds the ``use_uuid_as_userid`` site property, by default False.

- If email as login is already used in the site, we set
  ``login_transform`` to ``lower``.  This could give an error and quit
  the installation.  Maybe we want to catch this and just log a
  warning.

- It explicitly enables email as login name.  This would *not* be done
  when merging this package back to core Plone.
