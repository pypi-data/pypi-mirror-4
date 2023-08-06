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
    