============
Meta-recipes
============

Buildout recipes provide reusable Python modules for common
configuration tasks. The most widely used recipes tend to provide
low-level functions, like installing eggs or software distributions,
creating configuration files, and so on.  The normal recipe framework
is fairly well suited to building these general components.

Full-blown applications may require many, often tens, of parts.
Defining the many parts that make up an application can be tedious and
often entails a lot of repetition.  Buildout provides a number of
mechanisms to avoid repetition, including merging of configuration
files and macros, but these, while useful to an extent, don't scale
very well.  Buildout isn't and shouldn't be a programming language.

Meta-recipes allow us to bring Python to bear to provide higher-level
abstractions for buildouts.

A meta-recipe is a regular Python recipe that primarily operates by
creating parts.  A meta recipe isn't merely a high level recipe.  It's
a recipe that defers most of it's work to lower-level recipe by
manipulating the buildout database.

Unfortunately, buildout doesn't yet provide a high-level API for
creating parts.  It has a private low-level API which has been
promoted to public (meaning it won't be broken by future release), and
it's straightforward to write the needed high-level API, but it's
annoying to repeat the high-level API in each meta recipe.

This small package provides the high-level API needed for meta recipes
and a simple testing framework.  It will be merged into a future
buildout release.

A `presentation at PyCon 2011
<http://blip.tv/pycon-us-videos-2009-2010-2011/pycon-2011-deploying-applications-with-zc-buildout-4897770>`_
described early work with meta recipes.

.. contents::

A simple meta-recipe example
============================

Let's look at a fairly simple meta-recipe example.  First, consider a
buildout configuration that builds a database deployment::

  [buildout]
  parts = ctl pack

  [deployment]
  recipe = zc.recipe.deployment
  name = ample
  user = zope

  [ctl]
  recipe = zc.recipe.rhrc
  deployment = deployment
  chkconfig = 345 99 10
  parts = main

  [main]
  recipe = zc.zodbrecipes:server
  deployment = deployment
  address = 8100
  path = /var/databases/ample/main.fs
  zeo.conf =
     <zeo>
        address ${:address}
     </zeo>
     %import zc.zlibstorage
     <zlibstorage>
       <filestorage>
          path ${:path}
       </filestorage>
     </zlibstorage>

  [pack]
  recipe = zc.recipe.deployment:crontab
  deployment = deployment
  times = 1 2 * * 6
  command = ${buildout:bin-directory}/zeopack -d3 -t00 ${main:address}

.. -> low_level

This buildout doesn't build software. Rather it builds configuration
for deploying a database configuration using already-deployed
software.  For the purpose of this document, however, the details are
totally unimportant.

Rather than crafting the configuration above every time, we can write
a meta-recipe that crafts it for us.  We'll use our meta-recipe as
follows::

  [buildout]
  parts = ample

  [ample]
  recipe = com.example.ample:db
  path = /var/databases/ample/main.fs

The idea here is that the meta recipe allows us to specify the minimal
information necessary.  A meta-recipe often automates policies and
assumptions that are application and organization dependent.  The
example above assumes, for example, that we want to pack to 3
days in the past on Saturdays.

So now, let's see the meta recipe that automates this::

  import zc.metarecipe

  class Recipe(zc.metarecipe.Recipe):

      def __init__(self, buildout, name, options):
          super(Recipe, self).__init__(buildout, name, options)

          self.parse('''
              [deployment]
              recipe = zc.recipe.deployment
              name = %s
              user = zope
              ''' % name)

          self['main'] = dict(
              recipe = 'zc.zodbrecipes:server',
              deployment = 'deployment',
              address = 8100,
              path = options['path'],
              **{
                'zeo.conf': '''
                  <zeo>
                    address ${:address}
                  </zeo>

                  %import zc.zlibstorage

                  <zlibstorage>
                    <filestorage>
                      path ${:path}
                    </filestorage>
                  </zlibstorage>
                  '''}
              )

          self.parse('''
              [pack]
              recipe = zc.recipe.deployment:crontab
              deployment = deployment
              times = 1 2 * * 6
              command =
                ${buildout:bin-directory}/zeopack -d3 -t00 ${main:address}

              [ctl]
              recipe = zc.recipe.rhrc
              deployment = deployment
              chkconfig = 345 99 10
              parts = main
              ''')

.. -> source

    >>> exec source

The meta recipe just adds parts to the buildout. It does this by
calling inherited __setitem__ and ``parse`` methods.  The ``parse``
method just takes a string in ``ConfigParser`` syntax.  It's useful
when we want to add static, or nearly static part data.  The setitem
syntax is useful when we have non-trivial computation for part data.

The order that we add parts is important.  When adding a part, any
string substitutions and other dependencies are evaluated, so the
referenced parts must be defined first.  This is why, for example, the
``pack`` part is added after the ``main`` part.

Note that the meta recipe supplied an integer for one of the
options. In addition to strings, it's legal to supply integer and
unicode values.

Testing
=======

Now, let's test it.  We'll test it without actually running
buildout. Rather, we'll use a faux buildout provided by the
zc.metarecipe.testing module.

    >>> import zc.metarecipe.testing
    >>> buildout = zc.metarecipe.testing.Buildout()

    >>> _ = Recipe(buildout, 'ample', dict(path='/var/databases/ample/main.fs'))
    [deployment]
    name = ample
    recipe = zc.recipe.deployment
    user = zope
    [main]
    address = 8100
    deployment = deployment
    path = /var/databases/ample/main.fs
    recipe = zc.zodbrecipes:server
    zeo.conf = <zeo>
                        address ${:address}
                      </zeo>
    <BLANKLINE>
                      %import zc.zlibstorage
    <BLANKLINE>
                      <zlibstorage>
                        <filestorage>
                          path ${:path}
                        </filestorage>
                      </zlibstorage>
    [ctl]
    chkconfig = 345 99 10
    deployment = deployment
    parts = main
    recipe = zc.recipe.rhrc
    [pack]
    command = ${buildout:bin-directory}/zeopack -d3 -t00 ${main:address}
    deployment = deployment
    recipe = zc.recipe.deployment:crontab
    times = 1 2 * * 6

When we call our recipe, it will add sections to the test buildout and
these are simply printed as added, so we can verify that the correct
data was generated.

That's pretty much it.

Changes
=======

0.2.0 (2012-09-24)
------------------

- When setting option values, unicode and int values will be converted
  to strings.  Other non-string values are rejected.  Previously, it
  was easy to get errors from buildout when setting options with
  values read from ZooKeeper trees, which are unicode due to the use
  of JSON.

- Fixed: When using the meta-recipe parse method, the order that
  resulting sections were added was non-deterministic, due to the
  way ConfigParser works.  Not sections are added to a buildout
  in sortd order, by section name.

0.1.0 (2012-05-31)
------------------

Initial release
