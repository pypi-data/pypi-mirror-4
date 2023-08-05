def extend_parser(parser):

    parser.add_option(
        '--install-requirement-or-url',
        dest='installRequirementOrUrl',
        default='kforge',
        help="Install specific KForge package (e.g. kforge==0.16). The default is 'kforge'.")

    parser.add_option(
        '--domainmodel-requirement-or-url',
        dest='domainmodelRequirementOrUrl',
        default='',
        help="Install specific DomainModel package. The default is to defer to the requirements of the installed KForge package.")

    parser.add_option(
        '--extra-requirement-or-url',
        dest='extraRequirementOrUrl',
        default='',
        help="Install specific Python package.")

    parser.add_option(
        '--skip-service-setup',
        dest='skipServiceSetup',
        action='store_true',
        help="""Install system software, but skip service setup.""")

    parser.add_option(
        '--service-name',
        dest='serviceName',
        help="The service name to be used. The default is 'KForge'.")

    parser.add_option(
        '--password-digest-secret',
        dest='passwordDigestSecret',
        help='The "secret key" (used as "salt" for message digests). Use the old system value when upgrading.')

    parser.add_option(
        '--environment-timezone',
        dest='environmentTimezone',
        help="The timezone to be used. The default is 'Europe/London'.")

    parser.add_option(
        '--project-data-dir',
        dest='projectDataDir',
        help="""The folder to be used for project service data.
Please note that it can be worth setting this path outside of
the KFORGE_DIR path, since new versions of KForge will be installed
to another KFORGE_DIR but will need to use the same project services
data folder, which cannot be moved once created.
""")
    parser.add_option(
        '--db-user',
        dest='dbUser',
        help="The database user to be used. The default is 'kforge'.")

    parser.add_option(
        '--db-pass',
        dest='dbPass',
        help="The database user password. The default is ''.")

    parser.add_option(
        '--db-super-user',
        dest='dbSuperUser',
        help="The database super user (used for creating and deleting databases).")

    parser.add_option(
        '--db-super-pass',
        dest='dbSuperPass',
        help="The database super user password (used for creating and deleting databases.")

    parser.add_option(
        '--db-name',
        dest='dbName',
        help="""The database instance to be used. The default is 'kforge'.\n
Please note that if the --db-user, --db-pass, and --db-name options are all
set, then the installer will attempt to create the database and Apache 
configuration file. Otherwise, instructions for completing the installation
will be printed out at the end of the installation.
""")

    parser.add_option(
        '--db-type',
        dest='dbType',
        help="""The database type to be used. The choices are 'sqlite',
'postgres' or 'mysql'. The default is 'sqlite'.""")

    parser.add_option(
        '--db-host',
        dest='dbHost',
        help="""The database host to be used. The default is 'localhost'.""")

    parser.add_option(
        '--skip-db-create',
        dest='skipDbCreate',
        action='store_true',
        help="""Use existing database (if db user is not a db superuser).""")

    parser.add_option(
        '--skip-db',
        dest='skipDb',
        action='store_true',
        help="""Skip all database steps. The Apache configuration file 
creation step will also be skipped. Both the database and the Apache
configuration file are required for a working KForge instance.""")

    parser.add_option(
        '--dump-file',
        dest='dumpFile',
        help="""Initial domain data file to be used. You can dump data from a
previous version of KForge with the 'kforge-admin db dump DUMPFILE' command.""")


import os, subprocess, glob
def after_install(options, home_dir):


    # If necessary, install Python database bindings.
    if options.dbType == 'postgres':
        # If necessary download and install psycopg2.
        if options.no_site_packages:
            do_install_psycopg2 = True
            print "Not using global site packages, so will install psycopg2."
        else:
            try:
                print "Trying to import psycopg2 package......"
                call_subprocess([join(home_dir, 'bin', 'python'), 
                    '-c', 'import psycopg'], show_stdout=True)
            except OSError:
                print "Can't import psycopg2, will install psycopg2."
                do_install_psycopg2 = True
            else:
                print "Imported psycopg2 OK."
                do_install_psycopg2 = False
        if do_install_psycopg2:
            print "Attempting to install psycopg2..."
            # If necessary download and install egenix-mx-base.
            try:
                print "Trying to import mx.DateTime package......"
                call_subprocess([join(home_dir, 'bin', 'python'), 
                    '-c', 'import mx.DateTime'], show_stdout=True)
            except OSError:
                print "Can't import mx.DateTime, will install egenix-mx-base."
                do_install_egenix = True
            else:
                print "Imported mx.DateTime OK."
                do_install_egenix = False
            if do_install_egenix:
                print "Attempting to install egenix-mx-base from source..."
                egenix_version = '3.2.0'
                egenix_download_url = 'http://downloads.egenix.com/python/egenix-mx-base-%s.tar.gz' % egenix_version
                egenix_archive_path = 'egenix-mx-base-%s.tar.gz' % egenix_version
                egenix_source_path = 'egenix-mx-base-%s' % egenix_version
                print "Downloading %s" % egenix_download_url
                call_subprocess(['curl', egenix_download_url, '-o', egenix_archive_path], show_stdout=True)
                print "Extracting %s" % egenix_archive_path
                call_subprocess(['tar', 'zxvf', egenix_archive_path], show_stdout=False)
                python_bin_path = join(os.path.abspath(home_dir), 'bin', 'python')
                print "Installing %s" % egenix_source_path
                call_subprocess([python_bin_path, 'setup.py', 'install'], cwd=egenix_source_path, show_stdout=True)
                os.remove(egenix_archive_path)
                rmtree(egenix_source_path)
            try:
                call_subprocess([join(home_dir, 'bin', 'pip'), 'install', 'psycopg2'], show_stdout=True)
            except OSError, inst:
                msg = "Can't install psycopg2: %s" % inst
                msg += "\n\nAre development files for PostgreSQL installed?\n"
                raise Exception, msg
    elif options.dbType == 'mysql':
        # If necessary download and install mysql-python.
        if options.no_site_packages:
            do_install_MySQLdb = True
            print "Not using global site packages, so will install mysql-python."
        else:
            try:
                print "Trying to import MySQLdb package......"
                call_subprocess([join(home_dir, 'bin', 'python'), 
                    '-c', 'import MySQLdb'], show_stdout=True)
            except OSError:
                print "Can't import MySQLdb, will install mysql-python."
                do_install_MySQLdb = True
            else:
                print "Imported MySQLdb OK."
                do_install_MySQLdb = False
        if do_install_MySQLdb:
            print "Attempting to install mysql-python..."
            call_subprocess([join(home_dir, 'bin', 'pip'), 'install', 'mysql-python'], show_stdout=True)
    elif options.dbType == 'sqlite' or not  options.dbType:
        # If necessary download and install pysqlite.
        print "Trying to import pysqlite2, or sqlite3, or sqlite package......"
        do_install_pysqlite = False
        try:
            call_subprocess([join(home_dir, 'bin', 'python'), 
                '-c', 'import pysqlite2'], show_stdout=True)
        except OSError:
            print "Can't import pysqlite2, looking for sqlite3...."
            try:
                call_subprocess([join(home_dir, 'bin', 'python'), 
                    '-c', 'import sqlite3'], show_stdout=True)
            except OSError:
                print "Can't import sqlite3, looking for sqlite...."
                try:
                    call_subprocess([join(home_dir, 'bin', 'python'), 
                        '-c', 'import sqlite'], show_stdout=True)
                except OSError:
                    print "Can't import sqlite, will install pysqlite2...."
                    do_install_pysqlite = True
                else:
                    print "Imported sqlite OK."
            else:
                print "Imported sqlite3 OK."
        else:
            print "Imported pysqlite2 OK."
        if do_install_pysqlite:
            print "Attempting to install pysqlite..."
            call_subprocess([join(home_dir, 'bin', 'pip'), 'install', 'http://pypi.python.org/packages/source/p/pysqlite/pysqlite-2.5.6.tar.gz'], show_stdout=True)

    # If necessary, install old Markdown. Markdown 2.0.1 install fails due
    # to cElementTree when installed with easy_install and Python 2.4.
    # Update: Changed from easy_install to pip, but not sure whether above comment applies to pip.
    if sys.version_info[:2] == (2, 4):
        print "Pre-installing Markdown software"
        if subprocess.call([join(home_dir, 'bin', 'pip'), 'install', 'markdown==1.7']):
            print "Failed to pre-install Markdown software"
            sys.exit(2)
    else:
        # Just install it from download URL (freewisdom.org often down).
        if subprocess.call([join(home_dir, 'bin', 'pip'), 'install', 'http://pypi.python.org/packages/source/M/Markdown/Markdown-2.0.3.tar.gz']):
            print "Failed to pre-install Markdown software"
            sys.exit(2)

    # Install KForge Python package.
    arguments = options.extraRequirementOrUrl.split(' ')
    if options.extraRequirementOrUrl:
        for argument in options.extraRequirementOrUrl.split(' '):
            print "Pre-installing specific Python software (%s)." % argument
            if subprocess.call([join('bin', 'pip'), 'install', argument], cwd=home_dir):
                print "Failed to pre-install specific Python software (%s)." % argument
                sys.exit(2)
    argument = options.domainmodelRequirementOrUrl
    if argument:
        print "Pre-installing DomainModel software (%s)." % argument
        if subprocess.call([join('bin', 'pip'), 'install', argument], cwd=home_dir):
            print "Failed to pre-install DomainModel software."
            sys.exit(2)
    argument = options.installRequirementOrUrl
    if argument:
        print "Installing KForge software."
        if subprocess.call([join('bin', 'pip'), 'install', argument], cwd=home_dir):
            print "Failed to install KForge software."
            sys.exit(2)
    else:
        print "Error: No KForge requirement or URL."
        sys.exit(2)

    print "Installing ViewVC software."
    viewvc_download_url =  'http://viewvc.tigris.org/files/documents/3330/48814/viewvc-1.1.9.tar.gz'
    print "Downloading %s" % viewvc_download_url
    call_subprocess(['curl', '-O', viewvc_download_url], show_stdout=True, cwd=home_dir)
    viewvc_archive_path = viewvc_download_url.split('/')[-1]
    print "Extracting %s" % viewvc_archive_path
    call_subprocess(['tar', 'zxvf', viewvc_archive_path], show_stdout=False, cwd=home_dir)
    viewvc_install_path = viewvc_archive_path.replace('.tar.gz', '')

    print "Installing WsgiDAV software."
    argument = 'wsgidav'
    subprocess.call([join('bin', 'pip'), 'install', argument], cwd=home_dir)

    print "Installing Trac software."
    argument = 'trac==0.12.2'
    subprocess.call([join('bin', 'pip'), 'install', argument], cwd=home_dir)

    print "Installing Trac-Git software."
    if sys.version_info[:2] >= (2, 5):
        argument = 'http://trac-hacks.org/svn/gitplugin/0.12/'
        subprocess.call([join('bin', 'pip'), 'install', argument], cwd=home_dir)
    else:
        print "Not installing Trac-Git software. It doesn't work with Python 2.4."

    print "Installing Trac-Mercurial software."
    mercurial_archive_path = 'https://hg.edgewall.org/trac/mercurial-plugin#0.12'
    print "Cloning %s" % mercurial_archive_path
    call_subprocess(['hg', 'clone', mercurial_archive_path], show_stdout=False, cwd=home_dir)
    print "Running setup.py..."
    subprocess.call([join('..', 'bin', 'python'), 'setup.py', 'install'], cwd=join(home_dir, 'mercurial-plugin'))

    print "Installing Mercurial software."
    argument = 'mercurial'
    subprocess.call([join('bin', 'pip'), 'install', argument], cwd=home_dir)

    # Get path locations.
    home_dir, lib_dir, inc_dir, bin_dir = path_locations(home_dir)

    # Install KForge virtualenv Apache handlers.
    kforgevirtualenvhandlersPath = join(bin_dir, 'kforgevirtualenvhandlers.py')
    if not os.path.exists(kforgevirtualenvhandlersPath):
        activatethisPath = os.path.join(os.path.abspath(bin_dir), 'activate_this.py')
        # Todo: Pull this out of kforge.handlers.kforgevirtualenvhandlers.py.
        HANDLERS_PY = """# Code for virtualenv.
activatethisPath = "%s"
execfile(activatethisPath, dict(__file__=activatethisPath))

# KForge Apache 'access' handler.
try:
    from kforge.handlers.projecthost import accesshandler as accesshandler
except:
    pass

# KForge Apache 'authen' handler.
try:
    from kforge.handlers.projecthost import authenhandler as authenhandler
except:
    pass

# KForge Django handler
try:
    from django.core.handlers.modpython import handler as djangohandler
except:
    pass

# KForge Trac handler
try:
    from trac.web.modpython_frontend import handler as trachandler
except:
    try:
       # For Trac version < v0.9.
       import trac.ModPythonHandler as trachandler
    except:
       pass

    """ % activatethisPath
        writefile(kforgevirtualenvhandlersPath, HANDLERS_PY)
    if options.skipServiceSetup:
        print "Skipping service setup (by request)."
        print ""
        print "KForge system was installed OK. Steps to create a new KForge service:"
        print ""
        print "    $ source %s" % os.path.abspath(join(home_dir, 'bin', 'activate'))
        print ""
        print "1. Create a new KForge configuration file."
        print ""
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-makeconfig --help')
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-makeconfig [OPTIONS] PATH')
        print ""
        print "2. Set path to KForge configuration file in environment."
        print ""
        print "    (%s)$ export KFORGE_SETTINGS=PATH" % (os.path.basename(os.path.abspath(home_dir)))
        print ""
        print "3. Create and initialise the database."
        print ""
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin db create')
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin db init')
        print ""
        print "4. Generate the KForge Apache configuration file."
        print ""
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin apacheconfig create')
        print ""
        print "5. Print the path to the new KForge Apache configuration file."
        print ""
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin apacheconfig path')
        print ""
        print "6. Include the new KForge Apache configuration file in a virtual host of"
        print "your Apache server configuration, and check file permissions. Refer to"
        print "the KForge Install Guide for more information."
        return

    # Make KForge configuration file.
    print "Making new KForge configuration file."
    configPath = os.path.abspath(join(home_dir, 'etc', 'kforge.conf'))
    print configPath
    print ""
    mkdir(join(home_dir, 'etc'))
    mkdir(join(home_dir, 'var')) # Helps sqlite. :-)
    # gather kforge-makeconfig options
    masterDir = os.path.abspath(home_dir)
    arguments = []
    arguments.append("--%s=%s" % ('master-dir', masterDir))
    if options.serviceName != None:
        arguments.append("--%s=%s" % ('service-name', options.serviceName))
    if options.passwordDigestSecret != None:
        arguments.append("--%s=%s" % ('password-digest-secret', options.passwordDigestSecret))
    if options.environmentTimezone != None:
        arguments.append("--%s=%s" % ('environment-timezone', options.environmentTimezone))
    if options.projectDataDir != None:
        arguments.append("--%s=%s" % ('project-data-dir', options.projectDataDir))
    if options.dbUser != None:
        arguments.append("--%s=%s" % ('db-user', options.dbUser))
    if options.dbPass != None:
        arguments.append("--%s=%s" % ('db-pass', options.dbPass))
    if options.dbSuperUser != None:
        arguments.append("--%s=%s" % ('db-super-user', options.dbSuperUser))
    if options.dbSuperPass != None:
        arguments.append("--%s=%s" % ('db-super-pass', options.dbSuperPass))
    if options.dbName != None:
        arguments.append("--%s=%s" % ('db-name', options.dbName))
    if options.dbHost != None:
        arguments.append("--%s=%s" % ('db-host', options.dbHost))
    # Gently try to use SQLite, but "upgrade gracefully" if nudged.
    if options.dbType == None:
        if options.dbUser or options.dbPass or options.dbHost:
            arguments.append("--%s=%s" % ('db-type', 'postgres'))
        else:
            arguments.append("--%s=%s" % ('db-type', 'sqlite'))
            if not options.dbName:
                arguments.append("--%s=%s" % ('db-name', '%(master_dir)s/var/sqlite.db'))
    else:
        arguments.append("--%s=%s" % ('db-type', options.dbType))
        if options.dbType == 'sqlite' and not options.dbName:
            arguments.append("--%s=%s" % ('db-name', '%(master_dir)s/var/sqlite.db'))
    # Set KForge to work with the virtual environment.
    arguments.append("--%s=%s" % ('virtualenv-bin-dir',  os.path.abspath(join(home_dir, 'bin'))))
    # Set KForge to work with the newly installed ViewVC files.
    arguments.append("--%s=%s" % ('viewvc-dir',  os.path.abspath(join(home_dir, viewvc_install_path))))
    ## Set the newly install trac-admin script.
    if os.path.exists(os.path.abspath(join(home_dir, 'bin', 'trac-admin'))):
        arguments.append("--%s=%s" % ('trac-admin', '%(master_dir)s/bin/trac-admin'))
    ## Enable memoization.
    #arguments.append("--enable-memoization")
    # Final argument is the config path.
    arguments.append(configPath)
    # Call kforge-makeconfig with those arguments.
    cmd = [join(home_dir, 'bin', 'kforge-makeconfig')] + arguments
    print " ".join([c.replace(' ', '\ ') for c in cmd])
    call_subprocess(cmd)
    # Set config path in environment.
    os.environ['KFORGE_SETTINGS'] = configPath
    # Make KForge filesystem.
    print "Making new KForge template and media files."
    call_subprocess([join(home_dir, 'bin', 'kforge-admin'), 'fs', 'create'])
    if not options.skipDb:
        # Make KForge database.
        try:
            if options.skipDbCreate:
                print "Skipping creation of KForge database (by request)."
            else:
                print "Creating new KForge database instance."
                call_subprocess([join(home_dir, 'bin', 'kforge-admin'), 'db', 'create'])
            if options.dumpFile:
                print "Initialising KForge database from %s" % options.dumpFile
                call_subprocess([join(home_dir, 'bin', 'kforge-admin'), 'db', 'init', options.dumpFile])
            else:
                print "Initialising KForge database."
                call_subprocess([join(home_dir, 'bin', 'kforge-admin'), 'db', 'init'])
        except Exception, inst:
            print ""
            print "Error: %s" % str(inst)
            print ""
            # Todo: Make the exception traceback available (log file should be available).
            print "Sorry, couldn't create the database with the given values."
            print ""
            print "Steps to create the database and Apache configuration file:"
            print ""
            print "    $ source %s" % join(home_dir, 'bin', 'activate')
            print ""
            print "1. Please edit the KForge configuration file for your database"
            print "user, pass, and name. Create and initialise the database"
            print "by firstly activating the virual environment, and then running"
            print "the following kforge-admin commands:"
            print ""
            print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin db create')
            print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin db init')
            print ""
            print "2. Then, please generate the Apache configuration file by running"
            print "the following kforge-admin commands. The second command merely"
            print "shows the path to the new KForge Apache configuration file."
            print ""
            print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin apacheconfig create')
            print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin apacheconfig path')
            print ""
            print "3. Include the new KForge Apache configuration file in your"
            print "Apache server configuration, and check file permissions. Refer to "
            print "the KForge Install Guide for more information."
            sys.exit(2)
        else:
            # Make KForge Apache configuration file.
            print "Making new KForge Apache configuration file."
            call_subprocess([join(home_dir, 'bin', 'kforge-admin'), 'apacheconfig', 'create'])
            call_subprocess([join(home_dir, 'bin', 'kforge-admin'), 'apacheconfig', 'path'])
            print ""
            print "Please include the new KForge Apache configuration file in your "
            print "Apache server configuration, and check file permissions. Refer to "
            print "the KForge Install Guide for more information."
            print ""
            print "Looking for plugins to enable..."
            try:
                # Subversion.
                try:
                    call_subprocess(['which', 'svnadmin'], show_stdout=False, raise_on_returncode=True)
                except:
                    print "Subversion system not found."
                else:
                    print "Subversion system found. Enabling the Subversion plugin."
                    argument = 'plugin enable svn'
                    subprocess.call([join(home_dir, 'bin', 'kforge-admin'), argument])
                # Git.
                try:
                    call_subprocess(['which', 'git'], show_stdout=False, raise_on_returncode=True)
                except:
                    print "Git system not found."
                else:
                    print "Git system found. Enabling the Git plugin."
                    argument = 'plugin enable git'
                    subprocess.call([join(home_dir, 'bin', 'kforge-admin'), argument])
                # Mercurial.
                try:
                    call_subprocess(['which', 'hg'], show_stdout=False, raise_on_returncode=True)
                except:
                    print "Mercurial system not found."
                else:
                    print "Mercurial system found. Enabling the Mercurial plugin."
                    argument = 'plugin enable mercurial'
                    subprocess.call([join(home_dir, 'bin', 'kforge-admin'), argument])
                # Trac.
                try:
                    call_subprocess(['python', '-c' '"import trac"'], show_stdout=False, raise_on_returncode=True)
                except:
                    print "Trac system not found."
                else:
                #if os.path.exists(os.path.abspath(join(home_dir, 'bin', 'trac-admin'))):
                    print "Trac system found. Enabling the Trac plugin."
                    argument = 'plugin enable trac'
                    subprocess.call([join(home_dir, 'bin', 'kforge-admin'), argument])
            except Exception, inst:
                print "Error looking for plugins to enable: %s" % str(inst)
            print ""
            print "KForge was installed OK. Remember to set the path to your"
            print "config file when using 'kforge-admin':"
            print ""
            print "    $ export KFORGE_SETTINGS="+configPath
            print ""
            kforgeAdminPath = join(os.path.abspath(home_dir), 'bin', 'kforge-admin')
            print "    $ %s help plugin" % kforgeAdminPath 
            print "    $ %s plugin list" % kforgeAdminPath
            print "    $ %s plugin choices" % kforgeAdminPath
            print "    $ %s plugin enable ssh" % kforgeAdminPath
            print "    $ %s plugin show trac" % kforgeAdminPath
            print "    $ %s plugin disable dav" % kforgeAdminPath
            print ""
            print "Please note, 'kforge-admin' will be on your path if you "
            print "activate the virtualenv:"
            print ""
            print "    $ source %s" % os.path.abspath(join(home_dir, 'bin', 'activate'))
            print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin help plugin')
    else:
        print "Skipping creation and initialisation of KForge database (by request)."
        print "Skipping creation of KForge Apache configuration file (no database)."
        print ""
        print "KForge was installed OK. Please complete the installation by"
        print "by following the steps indicated below."
        print ""
        print "Steps to create the database and Apache configuration file:"
        print ""
        print "    $ source %s" % os.path.abspath(join(home_dir, 'bin', 'activate'))
        print ""
        print "1. Please edit the KForge configuration file for your database"
        print "user, pass, and name. Create and initialise the database"
        print ""
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin db create')
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin db init')
        print ""
        print "2. Please generate the Apache configuration file by running"
        print "the following kforge-admin commands. The second command merely"
        print "shows the path to the new KForge Apache configuration file."
        print ""
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin apacheconfig create')
        print "    (%s)$ %s" % (os.path.basename(os.path.abspath(home_dir)), 'kforge-admin apacheconfig path')
        print ""
        print "3. Include the new KForge Apache configuration file in your"
        print "Apache server configuration, and check file permissions. Refer to "
        print "the KForge Install Guide for more information."
    print ""

