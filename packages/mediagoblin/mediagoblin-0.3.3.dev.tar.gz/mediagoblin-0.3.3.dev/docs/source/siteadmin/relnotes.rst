.. MediaGoblin Documentation

   Written in 2012 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.

=============
Release Notes
=============

This chapter has important information for releases in it.
If you're upgrading from a previous release, please read it
carefully, or at least skim over it.

WIP
=====

**New features**

**Other changed**

* Plugin writers: Internal restructuring led to mediagoblin.db.sql* be
  mediagoblin.db.* starting from 0.3.3

* Dependency list has been reduced not requireing the "webob" package anymore.

0.3.2
=====

This will be the last release that is capable of converting from an earlier
MongoDB-based MediaGoblin instance to the newer SQL-based system.

**Do this to upgrade**

1. Make sure to run ``bin/gmg dbupdate`` after upgrading.


**New features**

* **3d model support!**

  You can now upload STL and OBJ files and display them in
  MediaGoblin.  Requires a recent-ish Blender; for details see:
  :ref:`deploying-chapter`

* **trim_whitespace**

  We bundle the optional plugin trim_whitespace which reduces the size
  of the delivered html output by reducing redundant whitespace.

  See :ref:`core-plugin-section` for plugin documentation

* **A new API!**

  It isn't well documented yet but we do have an API.  There is an
  `android application in progress <https://gitorious.org/mediagoblin/mediagoblin-android>`_
  which makes use of it, and there are some demo applications between
  `automgtic <https://github.com/jwandborg/automgtic>`_, an
  automatic media uploader for your desktop
  and `OMGMG <https://github.com/jwandborg/omgmg>`_, an example of
  a web application hooking up to the API.

  This is a plugin, so you have to enable it in your mediagoblin
  config file by adding a section under [plugins] like::

    [plugins]
    [[mediagoblin.plugins.api]]

  Note that the API works but is not nailed down... the way it is
  called may change in future releases.

* **OAuth login support**

  For applications that use OAuth to connect to the API.

  This is a plugin, so you have to enable it in your mediagoblin
  config file by adding a section under [plugins] like::

    [plugins]
    [[mediagoblin.plugins.oauth]]

* **Collections**

  We now have user-curated collections support.  These are arbitrary
  galleries that are customizable by users.  You can add media to
  these by clicking on the paperclip icon when logged in and looking
  at a media entry.

* **OpenStreetMap licensing display improvements**

  More accurate display of OSM licensing, and less disruptive: you
  click to "expand" the display of said licensing.

  Geolocation is also now on by default.

* **Miscelaneous visual improvements**

  We've made a number of small visual improvements including newer and
  nicer looking thumbnails and improved checkbox placement.



0.3.1
=====

**Do this to upgrade**

1. Make sure to run ``bin/gmg dbuptdate`` after upgrading.

2. If you set up your server config with an older version of
   mediagoblin and the mediagoblin docs, it's possible you don't
   have the "theme static files" alias, so double check to make
   sure that section is there if you are having problems.



**New features**

* **theming support**

  MediaGoblin now also includes theming support, which you can
  read about in the section :ref:`theming-chapter`.

* **flatpages**

  MediaGoblin has a flatpages plugin allowing you to add pages that
  are aren't media-related like "About this site...", "Terms of
  service...", etc.

  See :ref:`core-plugin-section` for plugin documentation


0.3.0
=====

This release has one important change. You need to act when
upgrading from a previous version!

This release changes the database system from MongoDB to
SQL(alchemy). If you want to setup a fresh instance, just
follow the instructions in the deployment chapter. If on
the other hand you want to continue to use one instance,
read on.

To convert your data from MongoDB to SQL(alchemy), you need
to follow these steps:

1. Make sure your MongoDB is still running and has your
   data, it's needed for the conversion.

2. Configure the ``sql_engine`` URI in the config to represent
   your target database (see: :ref:`deploying-chapter`)

3. You need an empty database.

4. Then run the following command::

       bin/gmg [-cf mediagoblin_config.ini] convert_mongo_to_sql

5. Start your server and investigate.

6. That's it.
