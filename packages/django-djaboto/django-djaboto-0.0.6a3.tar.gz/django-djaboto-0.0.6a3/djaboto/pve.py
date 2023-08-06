from subprocess import check_call
import os
from shutil import rmtree


def install_pve(pve_dir, leave_existing=True):
    """
    Install a fresh Python Virtual Environment
    """

    if os.path.isdir(pve_dir):
        if leave_existing:
            print "...leaving environment as is!"
        else:
            print '...removing %s and installing a fresh Python virtual environment' % pve_dir
            rmtree(pve_dir)
            check_call(['virtualenv', pve_dir])
    else:
        print '...installing Python virtual environment in %s ' % pve_dir
        check_call(['virtualenv', pve_dir])

def activate(pve_dir):
    activate_this = os.path.join(pve_dir, "bin", "activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))

def install_pve_base(cache_dir):
    print "...installing django-djaboto via pip"
    check_call(['pip', 'install', 'git+https://bitbucket.org/oddotterco/django-djaboto.git#egg=django-djaboto'])
    print "...installing django via pip"
    check_call(['pip', 'install', '--upgrade', '--download-cache=%s' % cache_dir, '--source=%s' % cache_dir, 'Django'])
    print "...upgrading distribute"
    check_call(['pip', 'install', '--upgrade', '--download-cache=%s' % cache_dir, '--source=%s' % cache_dir, 'distribute>=0.6.30'])
    print "...upgrading/installing MySQL-python"
    check_call(['pip', 'install', '--upgrade', '--download-cache=%s' % cache_dir, '--source=%s' % cache_dir, 'MySQL-python==1.2.3'])

def check_requirements(requirements_path):
    """
    Check all requirements and respond on mismatched ones
    """

    from pkg_resources import WorkingSet, DistributionNotFound, VersionConflict
    from setuptools.command.easy_install import main as install


    with open(requirements_path) as f_in:
        requirements = (line.rstrip() for line in f_in)
        requirements = (line for line in requirements if line[0]!='#') # Non-comment lines
        requirements = (line for line in requirements if not line.startswith('hg+')) # Non-hg+ lines
        requirements = (line for line in requirements if not line.startswith('git+')) # Non-hg+ lines
        requirements = list(line for line in requirements if line)

    working_set = WorkingSet()

    for requirement in requirements:

        if not requirement or requirement[0]=='#':
            continue

        ## Detecting if module is installed
        try:
            dep = working_set.require(requirement)
        except DistributionNotFound:
            print "DistributionNotFound for %s" % requirement
            #install([requirement])
        except VersionConflict, err:
            print "VersionConflict for %s" % requirement
            #install([requirement])
        #except Exception, err:
        #    print err
        #else:
        #    print "%s is currently installed. %s" % (requirement, dep[0])


    # Printing all installed modules
    #from pprint import pprint
    #pprint(tuple(working_set))


