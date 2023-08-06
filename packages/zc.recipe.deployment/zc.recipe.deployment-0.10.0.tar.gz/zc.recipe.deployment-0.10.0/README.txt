***********************
Unix Deployment Support
***********************

.. contents::

The zc.recipe.deployment recipe provides support for deploying
applications with multiple processes on Unix systems.  (Perhaps support
for other systems will be added later.)  It creates directories to hold
application instance configuration, log and run-time files.  It also
sets or reads options that can be read by other programs to find out
where to place files:

``cache-directory``
    The name of the directory where application instances should write
    cached copies of replacable data.  This defaults to /var/cache/NAME,
    where NAME is the deployment name.

``crontab-directory``
    The name of the directory in which cron jobs should be placed.
    This defaults to /etc/cron.d.

``etc-directory``
    The name of the directory where configuration files should be
    placed.  This defaults to /etc/NAME, where NAME is the deployment
    name.

``var-prefix``
    The path of the directory where configuration should be stored for
    all applications.  This defaults to /etc.

``lib-directory``
    The name of the directory where application instances should write
    valuable data.  This defaults to /var/lib/NAME, where NAME is the
    deployment name.

``log-directory``
    The name of the directory where application instances should write
    their log files.  This defaults to /var/log/NAME, where NAME is the
    deployment name.

``logrotate-directory``
    The name of the directory where logrotate configuration files
    should be placed, typically, /etc/logrotate.d.

``run-directory``
    The name of the directory where application instances should put
    their run-time files such as pid files and inter-process
    communication socket files.  This defaults to /var/run/NAME, where
    NAME is the deployment name.

``rc-directory``
    The name of the directory where run-control scripts should be
    installed.  This defaults to /etc/init.d.

``var-prefix``
    The path of the directory where data should be stored for all
    applications.  This defaults to /var.

Directories traditionally placed in the /var hierarchy are created in
such a way that the directories are owned by the user specified in the
``user`` option and are writable by the user and the user's group.
Directories usually found in the /etc hierarchy are created owned by the
user specified by the ``etc-user`` setting (default to 'root') with the
same permissions

A system-wide configuration file, zc.recipe.deployment.cfg, located in
the ``etc-prefix`` directory, can be used to specify the ``var-prefix``
setting.  The file uses the Python-standard ConfigParser syntax::

    [deployment]
    var-prefix = /mnt/fatdisk

Note that the section name is not related to the name of the deployment
parts being built; this is a system-wide setting not specific to any
deployment.  This is useful to identify very large partitions where
control over /var itself is difficult to achieve.
