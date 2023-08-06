from subprocess import check_call
import os

def install_system():
    """
    Install OS specific modules as needed
    """

    print "...performing system updates"
    check_call(['sudo', 'apt-get', 'update', '-y'])
    check_call(['sudo', 'apt-get', 'dist-upgrade', '-y'])
    check_call(['sudo', 'apt-get', 'install', '-y', 'python-setuptools', 'python-dev', 'python-virtualenv', 'git-core', 'mercurial', 'gcc', 'unison', 'python-pip', 'node-less', 'libtidy-dev'])

    # Install Apache and necessary components
    check_call(['sudo', 'apt-get', 'install', '-y', 'apache2', 'libapache2-mod-wsgi'])

    # Install PIL support for Virtual Environment on 64 bit systems
    ###TODO: check if this IS a 64bit system before even trying to do this
    try:
        check_call(['sudo', 'apt-get', 'install', '-y', 'python-imaging', 'libjpeg62-dev', 'libjpeg62', 'libjpeg8'])
        if not os.path.lexists('/usr/lib/libz.so'):
            os.symlink('/usr/lib/x86_64-linux-gnu/libz.so', '/usr/lib/libz.so')
        if not os.path.lexists('/usr/lib/libjpeg.so'):
            os.symlink('/usr/lib/x86_64-linux-gnu/libjpeg.so', '/usr/lib/libjpeg.so')
    except:
        pass

    print '...adding MySQL components'
    check_call(['sudo', 'apt-get', 'install', '-y', 'mysql-server', 'mysql-client', 'python-mysqldb', 'libmysqlclient-dev', 'build-essential', 'python-dev'])
