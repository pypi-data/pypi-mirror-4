###TODO: replace most sys.exit() calls to raise errors instead
###TODO: move all code from this command to libraries and connect aws command to the same calls

import optparse
import pip, xmlrpclib
import sys, os
from django.core.management.base import BaseCommand
import djaboto
from subprocess import check_call

class Command(BaseCommand):
    help = ("Check the status of your soupmix.")
    requires_model_validation = False
    can_import_settings = True

    option_list = BaseCommand.option_list + (
        optparse.make_option('-s', '--system',
            action='store_true',
            dest='check_system',
            help='check the current system environment for required modules and updates.',
        ),
        )

    def handle(self, *args, **options):
        """
        Checks the versions of installed packages and determines if there are new ones available
        Useful when updating the soupmix
        """

        if options.get('check_system', False):
            djaboto.debian.install_system()

        pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
        for dist in pip.get_installed_distributions():
            available = pypi.package_releases(dist.project_name)

            if not available:
                # Try to capitalize pkg name
                available = pypi.package_releases(dist.project_name.capitalize())

            if available and (available[0] != dist.version):
                msg = '{} available'.format(available[0])
                pkg_info = '{dist.project_name} {dist.version}'.format(dist=dist)
                print '{pkg_info:40} {msg}'.format(pkg_info=pkg_info, msg=msg)

def gitReady(target_dir, git_url=None):
    import git

    # If the target already exists, attempt to refresh it
    if os.path.isdir(target_dir):
        try:
            repository = git.Repo(target_dir)
            o = repository.remotes.origin
            o.pull()
        except:
            print "Error occured when attempting to refresh the git repository at %s" % target_dir
            sys.exit(1)
    else:
        if git_url:
            repository = git.Repo.clone_from(git_url, target_dir)

def execute():
    """
    Install the Soupmix
    """

    import argparse

    ###TODO: optionally load these from a settings file (~/.djaboto_conf)
    parser = argparse.ArgumentParser(
        description='Create, manage and publish an AWS hosted website.',
        epilog='',
        version=djaboto.get_version(),
    )
    parser.add_argument('-e','--existingpve',
        action="store_true",
        default=False,
        help='use current python environment as-is',
    )
    parser.add_argument('-s','--checksystem',
        action="store_true",
        default=False,
        help='check for required system libraries',
    )
    parser.add_argument('site_name',
        metavar='SITE_NAME',
        type=str,
        help='Site name to create.  i.e. "mysite".',
    )
    parser.add_argument('--basedir',
        metavar='BASE_DIR',
        type=str,
        default= os.path.expanduser('~/django'),
        help='Django projects base directory',
    )
    parser.add_argument('--cachedir',
        metavar='CACHE_DIR',
        type=str,
        default= os.path.expanduser('~/django/cache'),
        help='Python cache directory (to speed up repeated installations).',
    )
    parser.add_argument('--python',
        metavar='PYTHON_DIR',
        type=str,
        default= os.path.expanduser('~/django/python'),
        help='Python virtual environment installation directory.',
    )
    parser.add_argument('-t', '--template',
        metavar='SITE_TEMPLATE',
        type=str,
        default= os.path.expanduser('~/django/branding'),
        help='Site template source.  Can be a URL, directory or archive.',
    )
    parser.add_argument('-g', '--gitrepo',
        metavar='GIT_REPO',
        type=str,
        ###TODO: remove this default?  Shouldn't this be for testing only?
        # Yes - but only after we have something like a  ~/.djaboto config
        # file available so that we can still automate consistantly
        default= 'https://Growlf@bitbucket.org/oddotterco/branding.git',
        help='Git repository.',
    )

    args = parser.parse_args()
    origWD = os.getcwd()

    if args.checksystem:
        djaboto.debian.install_system()

    ## Create a nice home for our projects and tools if it is not there
    #  already. Everyone needs a home, with hot cocoa (spices later).
    DIR_BASE = os.path.realpath(args.basedir)
    if not os.path.isdir(DIR_BASE):
        os.mkdir(DIR_BASE)
        print "...created %s as base directory" % DIR_BASE
    else:
        print "...using %s as base directory" % DIR_BASE
    os.chdir(DIR_BASE)

    ## Create a backup cache directory to speed up re-installs if it is
    # not already present
    DIR_CACHE = os.path.realpath( args.cachedir )
    if not os.path.isdir(DIR_CACHE):
        os.mkdir( DIR_CACHE )
        print "...created %s as python module cache directory" % DIR_CACHE
    else:
        print "...using %s as python module cache directory" % DIR_CACHE

    ## Manage the virtual python freshness. New socks or old smelly ones
    # today...?
    DIR_PYTHON = os.path.realpath(args.python)
    djaboto.pve.install_pve(DIR_PYTHON, args.existingpve)
    djaboto.pve.activate(DIR_PYTHON)
    if not args.existingpve:
        djaboto.pve.install_pve_base(DIR_CACHE)

    ## Verify the template source or create it if we can
    print "...using %s as project template." % args.template
    if args.gitrepo:
        print "...giting %s." % args.gitrepo
        gitReady(args.template, args.gitrepo,)

    ## Name the project directory and warn if it already exists
    DIR_PROJECT = os.path.join(DIR_BASE, args.site_name)
    print '...using %s as project target directory' % DIR_PROJECT
    if os.path.isdir(DIR_PROJECT):
        print 'That directory already exists.  Please choose a new one.'
        exit(0)

    ## Create the base project structure using the built-in commands from
    # Django after changing directories accordingly
    print "...start project using django-admin.py"
    check_call(['django-admin.py','startproject','--template',args.template,'-e','conf',args.site_name])

    ## Install required modules
    REQ_TXT = os.path.join(DIR_PROJECT, "requirements.txt")
    print "...installing requirements as specified by %s" % REQ_TXT
    if not args.existingpve:
        check_call(['pip', 'install', '--upgrade', '--download-cache=%s' % DIR_CACHE, '--source=%s' % DIR_CACHE, '-r', REQ_TXT])
    else:
        check_call(['pip', 'install', '--download-cache=%s' % DIR_CACHE, '--source=%s' % DIR_CACHE, '-r', REQ_TXT])

    ## Create the site's database, dropping any existing if needed
    print "...clear and rebuild a fresh database for %s" % args.site_name
    from _mysql import connect as mysql_connect
    mysql_loc_pwd = raw_input("Password for your MySQL root account? ")
    mysql_rmt_pwd = raw_input("Password for your website sql user? ")
    ###TODO: should probably check if we really want to drop the existing database first
    db=mysql_connect(user="root",passwd=mysql_loc_pwd)
    db.query("DROP DATABASE IF EXISTS django_%s;" % args.site_name)
    db.query("CREATE DATABASE django_%s;" % args.site_name)
    db.query("GRANT ALL ON django_%s.* TO \'djangouser\'@\'localhost\' IDENTIFIED BY \'%s\';" % (args.site_name, mysql_rmt_pwd))

    ## Manage.py sync, migrate, collectstatic
    DIR_STATIC = os.path.join(DIR_PROJECT, args.site_name, 'static')
    os.chdir(DIR_PROJECT)

    print '...making manage.py executable'
    check_call(['chmod','+x','manage.py'])

    print '...running syncdb via manage.py'
    check_call(['./manage.py','syncdb'])

    print '...running migrate via manage.py with no input'
    check_call(['./manage.py','migrate','--noinput'])

    print '...running collectstatic -l via manage.py with no input'
    check_call(['./manage.py','collectstatic','-l','--noinput'])

    print '...fixing static directory permissions'
    check_call(['sudo', 'chown', '-R', ':www-data', DIR_STATIC])
    check_call(['sudo', 'chmod', '-R', 'ug+rw', DIR_STATIC])

    # Back to where we started from
    os.chdir(origWD)



# For an "entrypoint" style command to Django command access, create something like the
# following in the django commandfile in an execute() definition:
#
# from django.conf import settings
# def execute():
#   settings.configure()
#   cmd = Command()
#   cmd.execute(["<label>" [, args]])
#
# The in the setup.py add:
#entry_points = {
#               'console_scripts': [
#                   '<script_or_command_name> = <path.to.django_command.file>:execute',
#                   ],
#               },

