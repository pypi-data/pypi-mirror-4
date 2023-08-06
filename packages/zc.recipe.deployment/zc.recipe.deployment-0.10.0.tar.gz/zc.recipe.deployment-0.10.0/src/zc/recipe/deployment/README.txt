Using the deployment recipe is pretty simple.  Just specify a
deployment name, specified via the part name, and a deployment user.

Let's add a deployment to a sample buildout:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... prefix = %s
    ... recipe = zc.recipe.deployment
    ... user = %s
    ... etc-user = %s
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/cache/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/lib/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'

Note that we are providing a prefix and an etc-user here.  These options
default to '/' and 'root', respectively.

Now we can see that directories named foo in PREFIX/etc, PREFIX/var/log and
PREFIX/var/run have been created:

    >>> import os
    >>> print ls(os.path.join(sample_buildout, 'etc/foo'))
    drwxr-xr-x USER GROUP PREFIX/etc/foo

    >>> print ls(os.path.join(sample_buildout, 'var/cache/foo'))
    drwxr-xr-x USER GROUP PREFIX/var/cache/foo

    >>> print ls(os.path.join(sample_buildout, 'var/lib/foo'))
    drwxr-xr-x USER GROUP PREFIX/var/lib/foo

    >>> print ls(os.path.join(sample_buildout, 'var/log/foo'))
    drwxr-xr-x USER GROUP PREFIX/var/log/foo

    >>> print ls(os.path.join(sample_buildout, 'var/run/foo'))
    drwxr-x--- USER GROUP PREFIX/var/run/foo

By looking at .installed.cfg, we can see the options available for use
by other recipes:

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [buildout]
    ...
    [foo]
    __buildout_installed__ =
    ...
    cache-directory = PREFIX/var/cache/foo
    crontab-directory = PREFIX/etc/cron.d
    etc-directory = PREFIX/etc/foo
    etc-prefix = PREFIX/etc
    etc-user = USER
    lib-directory = PREFIX/var/lib/foo
    log-directory = PREFIX/var/log/foo
    logrotate-directory = PREFIX/etc/logrotate.d
    name = foo
    prefix = PREFIX
    rc-directory = PREFIX/etc/init.d
    recipe = zc.recipe.deployment
    run-directory = PREFIX/var/run/foo
    user = USER
    var-prefix = PREFIX/var

If we uninstall, then the directories are removed.

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/cache/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/lib/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.

    >>> import os
    >>> os.path.exists(os.path.join(sample_buildout, 'etc/foo'))
    False
    >>> os.path.exists(os.path.join(sample_buildout, 'var/cache/foo'))
    False
    >>> os.path.exists(os.path.join(sample_buildout, 'var/lib/foo'))
    False
    >>> os.path.exists(os.path.join(sample_buildout, 'var/log/foo'))
    False
    >>> os.path.exists(os.path.join(sample_buildout, 'var/run/foo'))
    False

The cache, lib, log and run directories are only removed if they are empty.
To see that, we'll put a file in each of the directories created:

    >>> print system(join('bin', 'buildout')),
    ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/cache/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/lib/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'

    >>> write(os.path.join(sample_buildout, 'etc/foo/x'), '')
    >>> write(os.path.join(sample_buildout, 'var/cache/foo/x'), '')
    >>> write(os.path.join(sample_buildout, 'var/lib/foo/x'), '')
    >>> write(os.path.join(sample_buildout, 'var/log/foo/x'), '')
    >>> write(os.path.join(sample_buildout, 'var/run/foo/x'), '')

And then uninstall:

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Can't remove non-empty directory 'PREFIX/var/cache/foo'.
    zc.recipe.deployment: Can't remove non-empty directory 'PREFIX/var/lib/foo'.
    zc.recipe.deployment: Can't remove non-empty directory 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Can't remove non-empty directory 'PREFIX/var/run/foo'.

    >>> os.path.exists(os.path.join(sample_buildout, 'etc/foo'))
    False

    >>> print ls(os.path.join(sample_buildout, 'var/cache/foo'))
    drwxr-xr-x USER GROUP PREFIX/var/cache/foo

    >>> print ls(os.path.join(sample_buildout, 'var/lib/foo'))
    drwxr-xr-x USER GROUP PREFIX/var/lib/foo

    >>> print ls(os.path.join(sample_buildout, 'var/log/foo'))
    drwxr-xr-x USER GROUP PREFIX/var/log/foo

    >>> print ls(os.path.join(sample_buildout, 'var/run/foo'))
    drwxr-x--- USER GROUP PREFIX/var/run/foo

Here we see that the var and run directories are kept.  The etc
directory is discarded because only buildout recipes should write to
it and all of its data are expendible.

If we reinstall, remove the files, and uninstall, then the directories
are removed:

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Updating 'PREFIX/var/cache/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Updating 'PREFIX/var/lib/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Updating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Updating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'

    >>> os.remove(os.path.join(sample_buildout, 'var/cache/foo/x'))
    >>> os.remove(os.path.join(sample_buildout, 'var/lib/foo/x'))
    >>> os.remove(os.path.join(sample_buildout, 'var/log/foo/x'))
    >>> os.remove(os.path.join(sample_buildout, 'var/run/foo/x'))

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/cache/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/lib/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.

    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/etc/foo'))
    False
    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/var/cache/foo'))
    False
    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/var/lib/foo'))
    False
    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/var/log/foo'))
    False
    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/var/run/foo'))
    False


Deployment Name
===============

The deployment name is used for naming generated files and directories.
The deployment name defaults to the section name, but the deployment
name can be specified explicitly:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... name = bar
    ... user = %s
    ... etc-user = %s
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/cache/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/lib/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/log/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/run/bar',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'

    >>> print ls(os.path.join(sample_buildout, 'etc/bar'))
    drwxr-xr-x USER GROUP PREFIX/etc/bar

    >>> print ls(os.path.join(sample_buildout, 'var/cache/bar'))
    drwxr-xr-x USER GROUP PREFIX/var/cache/bar

    >>> print ls(os.path.join(sample_buildout, 'var/lib/bar'))
    drwxr-xr-x USER GROUP PREFIX/var/lib/bar

    >>> print ls(os.path.join(sample_buildout, 'var/log/bar'))
    drwxr-xr-x USER GROUP PREFIX/var/log/bar

    >>> print ls(os.path.join(sample_buildout, 'var/run/bar'))
    drwxr-x--- USER GROUP PREFIX/var/run/bar

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [buildout]
    installed_develop_eggs =
    parts = foo
    <BLANKLINE>
    [foo]
    __buildout_installed__ =
    ...
    cache-directory = PREFIX/var/cache/bar
    crontab-directory = PREFIX/etc/cron.d
    etc-directory = PREFIX/etc/bar
    etc-prefix = PREFIX/etc
    etc-user = USER
    lib-directory = PREFIX/var/lib/bar
    log-directory = PREFIX/var/log/bar
    logrotate-directory = PREFIX/etc/logrotate.d
    name = bar
    prefix = PREFIX
    rc-directory = PREFIX/etc/init.d
    recipe = zc.recipe.deployment
    run-directory = PREFIX/var/run/bar
    user = USER
    var-prefix = PREFIX/var

Note (here and earlier) that the options include the name option,
which defaults to the part name.  Other parts that use the deployment
name should use the name option rather than the part name.


Configuration files
===================

Normally, configuration files are created by specialized recipes.
Sometimes, it's useful to specify configuration files in a buildout
configuration file.  The zc.recipe.deployment:configuration recipe can be
used to do that.

Let's add a configuration file to our buildout:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/bar'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/cache/bar'.
    zc.recipe.deployment: Removing 'PREFIX/var/lib/bar'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/bar'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/bar'.
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/cache/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/lib/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'
    Installing x.cfg.

By default, the configuration is installed as a part:

    >>> cat('parts', 'x.cfg')
    xxx
    yyy
    zzz

If a deployment is specified, then the file is placed in the
deployment etc directory:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.
    zc.recipe.deployment:
        Updating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'

    >>> os.path.exists(join('parts', 'x.cfg'))
    False

    >>> cat(os.path.join(sample_buildout, 'etc/foo/x.cfg'))
    xxx
    yyy
    zzz

If a directory is specified, then the file is placed in the directory.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... directory = etc/foobar
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/foobar',
        mode 755, user 'USER', group 'GROUP'

    >>> os.path.exists(join('parts', 'x.cfg'))
    False
    >>> os.path.exists(join(sample_buildout, 'etc/foo/x.cfg'))
    False

    >>> cat(os.path.join(sample_buildout, 'etc/foobar/x.cfg'))
    xxx
    yyy
    zzz

A directory option works only with a deployment option.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... directory = etc/foobar
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.

    >>> os.path.exists(join('parts', 'x.cfg'))
    True
    >>> os.path.exists(join(sample_buildout, 'etc/foobar/x.cfg'))
    False

    >>> cat('parts', 'x.cfg')
    xxx
    yyy
    zzz

We can read data from a file rather than specifying in the
configuration:

    >>> write('x.in', '1\n2\n3\n')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... file = x.in
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.
    zc.recipe.deployment:
        Updating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'

    >>> cat(os.path.join(sample_buildout, 'etc/foo/x.cfg'))
    1
    2
    3

The recipe sets a location option that can be used by other recipes:

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS
    [buildout]
    ...
    [x.cfg]
    ...
    location = PREFIX/etc/foo/x.cfg
    ...


Cron support
============

The crontab recipe provides support for creating crontab files.  It
uses a times option to specify times to run the command and a command
option containing the command.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo cron
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing cron.

This example creates PREFIX/etc/cron.d/foo-cron

    >>> open(os.path.join(sample_buildout, 'etc/cron.d/foo-cron')).read()
    '30 23 * * *\tUSER\techo hello world!\n'

.. make sure cron recipe honors deployment name option:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo cron
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... name = bar
    ... user = %s
    ... etc-user = %s
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/cache/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/lib/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/cache/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/lib/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/log/bar',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/run/bar',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'
    Installing cron.

    >>> open(os.path.join(sample_buildout, 'etc/cron.d/bar-cron')).read()
    '30 23 * * *\tUSER\techo hello world!\n'

The crontab recipe gets its  user from the buildout's deployment by default,
but it doesn't have to.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo cron
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... name = bar
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... user = bob
    ... command = echo hello world!
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling cron.
    Updating foo.
    Installing cron.

    >>> open('etc/cron.d/bar-cron').read()
    '30 23 * * *\tbob\techo hello world!\n'


.. edge case

    uninstall with no stored prefix

    >>> installed = [l for l in open('.installed.cfg')
    ...              if not l.startswith('prefix =')]
    >>> open('.installed.cfg', 'w').write(''.join(installed))

    uninstall with some directories already gone:

    >>> rmdir(sample_buildout, 'etc', 'bar')
    >>> rmdir(sample_buildout, 'var', 'run')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts =
    ... ''')

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/var/cache/bar'.
    zc.recipe.deployment: Removing 'PREFIX/var/lib/bar'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/bar'.


.. cleanup

    >>> print system(join('bin', 'buildout')+' buildout:parts='),

    >>> os.path.exists(os.path.join(sample_buildout, 'etc/cron.d/bar-cron'))
    False


SharedConfig
============

This recipe can be used to update configuration files that are shared by
multiple applications.  The absolute path of the file must be specified.
Also, the configuration files must accept comments that start with "#".

Like the configuration recipe, the content to add in the configuration file can
be provided using the "text" or the "file" option.

First let's create a file that will be used as the shared configuration file.

    >>> open('y.cfg', 'w').write(
    ... '''Some
    ... existing
    ... configuration
    ... ''')

We now create our buildout configuration and use the "sharedconfig" recipe and
run buildout.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo y.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [y.cfg]
    ... recipe = zc.recipe.deployment:sharedconfig
    ... path = y.cfg
    ... deployment = foo
    ... text = xxx
    ...        yyy
    ...        zzz
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/cache/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/lib/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Updating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Updating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Updating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'
    Installing y.cfg.

    >>> print open('y.cfg', 'r').read()
    Some
    existing
    configuration
    <BLANKLINE>
    #[foo_y.cfg DO NOT MODIFY LINES FROM HERE#
    xxx
    yyy
    zzz
    #TILL HERE foo_y.cfg]#
    <BLANKLINE>

Running buildout again without modifying the configuration leaves the file the
same.

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Updating foo.
    Updating y.cfg.

    >>> print open('y.cfg', 'r').read()
    Some
    existing
    configuration
    <BLANKLINE>
    #[foo_y.cfg DO NOT MODIFY LINES FROM HERE#
    xxx
    yyy
    zzz
    #TILL HERE foo_y.cfg]#
    <BLANKLINE>

If we add some more lines to the file

    >>> open('y.cfg', 'a').write(
    ... '''Some
    ... additional
    ... configuration
    ... ''')

and run buildout again, but this time after modifying the configuration for
"y.cfg", the sections will be moved to the end of the file.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo y.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [y.cfg]
    ... recipe = zc.recipe.deployment:sharedconfig
    ... path = y.cfg
    ... deployment = foo
    ... text = 111
    ...        222
    ...        333
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling y.cfg.
    Running uninstall recipe.
    Updating foo.
    Installing y.cfg.

    >>> print open('y.cfg', 'r').read()
    Some
    existing
    configuration
    Some
    additional
    configuration
    <BLANKLINE>
    #[foo_y.cfg DO NOT MODIFY LINES FROM HERE#
    111
    222
    333
    #TILL HERE foo_y.cfg]#
    <BLANKLINE>

The text to append to the shared configuration file can also be provided via a
file.

    >>> write('x.cfg', '''
    ... [foo]
    ... a = 1
    ... b = 2
    ...
    ... [log]
    ... c = 1
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo y.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [y.cfg]
    ... recipe = zc.recipe.deployment:sharedconfig
    ... path = %s/etc/z.cfg
    ... deployment = foo
    ... file = x.cfg
    ... ''' % (sample_buildout, user, user, sample_buildout))
    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    While:
      Installing.
      Getting section y.cfg.
      Initializing part y.cfg.
    Error: Path 'PREFIX/etc/z.cfg' does not exist

Oops. The path of the configuration file must exist. Let's create one.

    >>> write(join(sample_buildout, 'etc', 'z.cfg'), '')
    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling y.cfg.
    Running uninstall recipe.
    Updating foo.
    Installing y.cfg.

    >>> print open(join(sample_buildout, 'etc', 'z.cfg'), 'r').read()
    <BLANKLINE>
    #[foo_y.cfg DO NOT MODIFY LINES FROM HERE#
    <BLANKLINE>
    [foo]
    a = 1
    b = 2
    <BLANKLINE>
    [log]
    c = 1
    <BLANKLINE>
    #TILL HERE foo_y.cfg]#
    <BLANKLINE>

While uninstalling, only the lines that the recipe installed are removed.

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling y.cfg.
    Running uninstall recipe.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/cache/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/lib/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.

But the files are not deleted.

    >>> os.path.exists('y.cfg')
    True

    >>> print open('y.cfg', 'r').read()
    Some
    existing
    configuration
    Some
    additional
    configuration
    <BLANKLINE>

    >>> os.path.exists(join(sample_buildout, 'etc', 'z.cfg'))
    True

    >>> print open(join(sample_buildout, 'etc', 'z.cfg'), 'r').read()
    <BLANKLINE>


Edgecases
---------

The SharedConfig recipe checks to see if the current data in the file
ends with a new line.  If it doesn't exist it adds one.  This is in
addition to the blank line the recipe adds before the section to enhance
readability.

    >>> open('anotherconfig.cfg', 'w').write('one')
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo y.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [y.cfg]
    ... recipe = zc.recipe.deployment:sharedconfig
    ... path = anotherconfig.cfg
    ... deployment = foo
    ... text = I predict that there will be a blank line above this.
    ... ''' % (sample_buildout, user, user))
    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/cache/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/lib/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'GROUP'
    zc.recipe.deployment:
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'GROUP'
    Installing y.cfg.

    >>> print open('anotherconfig.cfg').read()
    one
    <BLANKLINE>
    #[foo_y.cfg DO NOT MODIFY LINES FROM HERE#
    I predict that there will be a blank line above this.
    #TILL HERE foo_y.cfg]#
    <BLANKLINE>

But the recipe doesn't add a new line if there was one already at the end.

    >>> open('anotherconfig.cfg', 'w').write('ends with a new line\n')
    >>> print open('anotherconfig.cfg').read()
    ends with a new line
    <BLANKLINE>

We modify the buildout configuration so that "install" is invoked again:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo y.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [y.cfg]
    ... recipe = zc.recipe.deployment:sharedconfig
    ... path = anotherconfig.cfg
    ... deployment = foo
    ... text = there will still be only a single blank line above.
    ... ''' % (sample_buildout, user, user))
    >>> print system(join('bin', 'buildout')), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling y.cfg.
    Running uninstall recipe.
    Updating foo.
    Installing y.cfg.

    >>> print open('anotherconfig.cfg').read()
    ends with a new line
    <BLANKLINE>
    #[foo_y.cfg DO NOT MODIFY LINES FROM HERE#
    there will still be only a single blank line above.
    #TILL HERE foo_y.cfg]#
    <BLANKLINE>

If we uninstall the file, the data will be the same as "original_data":

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling y.cfg.
    Running uninstall recipe.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/cache/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/lib/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.

    >>> print open('anotherconfig.cfg').read()
    ends with a new line
    <BLANKLINE>
