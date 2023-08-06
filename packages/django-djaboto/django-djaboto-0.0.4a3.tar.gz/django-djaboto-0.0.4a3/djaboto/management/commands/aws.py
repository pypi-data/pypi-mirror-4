# -*- coding: utf-8 -*-
import optparse
import os, sys
from os.path import isfile
from time import sleep
from fabric import operations as fab_op
from fabric import api as fab_api
from fabric import colors as fab_colors
from fabric.contrib.files import exists as fab_exists

from boto import config as BotoConfig, ec2, exception as BotoException

from urllib import urlencode
from urllib2 import Request
from urllib2 import urlopen

from base64 import b64encode
import json
from django.core.management.base import BaseCommand
import djaboto


PROJECT_TEMPLATES_DIR = os.path.join(os.path.dirname(djaboto.__file__), 'recipe')

###TODO: move all references to the target and source directories to a dynamic variable instead of hardcoded
###TODO: allow for commandline overrides of target and source directories
###TODO: streamline the sub-commands down to one or two that automatically perform all of the steps dynamically and 'as-needed'/specified

AWS_SETTINGS_PROMPTS = {
    'SITENAME':('Site name',''),
    'AWS_INSTANCE_ID':('AWS instance ID',''),
    'AWS_ACCESS_KEY_ID':('AWS Security Credentials, Access Key ID',''),
    'AWS_ACCESS_SECRET':('AWS Security Credentials, Secret Access Key',''),
    'AWS_REGION':('Amazon Region','us-west-1'),
    'AWS_TYPE':('Amazon Instance Type','t1.micro'),
    'AWS_AMI_ID':('AMI ID','ami-87712ac2'),
    'AWS_USER':('Instance default username','ubuntu'),
    'AWS_HTTPD_USER':('Apache user','www-data'),
    'AWS_HTTPD_GROUP':('Apache group','www-data'),
}

#noinspection PyBroadException,PyUnresolvedReferences
class Command(BaseCommand):
    """
    AWS command class
    """

    ###TODO: the help and args should indicate which commands are common and which rarely should be used
    ###TODO: use library "argh" instead of directly manipulating optparse. too verbose.

    args = '[settings|firewall|create|update|perms|apache|restart|reboot|shell|instance|keys|addkey|rmkey|ip|terminate]'
    help = """Manages the AWS account and settings in your project.

Issuing this command without arguments will provide a list of any available AWS instances.

Arguments (sub commands):
    create    - create the entire server and sync with the local file

    terminate- terminate and instance and remove from .aws_fabric
    keys     - list the IDs of keys installed on remote
    addkey   - add new keys to remote
    rmkey    - remove keys from remote
    ip       - get ip address of remote
    instance - create a bare instance and install your ssh key
    settings - show current settings values stored for this project
    firewall - create the AWS security groups
    update   - synchronize files between your local system and  the remote instance
    perms    - set permissions to default usable values on the remote instance
    apache   - create an Apache configuration file and enable it on the remote instance
    restart  - restart the remote Apache service
    reboot   - reboot the remote instance
    shell    - open a shell on the remote instance"""


    conn = ''
    instance = ''

    option_list = BaseCommand.option_list + (
        optparse.make_option('-d', '--domain',
            action='store',
            type='string',
            dest='domain',
            help='Domain-name of site (fqdn root, "mydomain.com")',
        ),
        optparse.make_option('--sitename',
            action='store',
            type='string',
            dest='sitename',
            help='Name of site (directory, "mysite")',
        ),
        optparse.make_option('--instance',
            action='store',
            type='string',
            dest='aws_instance_id',
            help='AWS instance ID',
        ),
        optparse.make_option('--awskeyid',
            action='store',
            type='string',
            dest='aws_access_key_id',
            help='AWS Security Credentials, Access Key ID',
        ),
        optparse.make_option('--awssecret',
            action='store',
            type='string',
            dest='aws_access_secret',
            help='AWS Security Credentials, Secret Access Key',
        ),
        optparse.make_option('--awsregion',
            action='store',
            type='string',
            dest='aws_region',
            default='us-west-1',
            help='Amazon Region',
        ),
        optparse.make_option('--awstype',
            action='store',
            type='string',
            dest='aws_type',
            default='t1.micro',
            help='Amazon Instance Type',
        ),
        optparse.make_option('--awsami',
            action='store',
            type='string',
            dest='aws_ami',
            default='ami-87712ac2',
            help='Amazon AMI ID',
        ),
        optparse.make_option('--sshpubkey',
            action='store',
            type='string',
            dest='aws_security_key',
            help='path to your SSH public key file',
        ),
        optparse.make_option('--awsuser',
            action='store',
            type='string',
            dest='aws_user',
            default='ubuntu',
            help='Instance username',
        ),
        optparse.make_option('--awshttpduser',
            action='store',
            type='string',
            dest='aws_httpd_user',
            default='www-data',
            help='Apache username',
        ),
        optparse.make_option('--awshttpdgroup',
            action='store',
            type='string',
            dest='aws_httpd_group',
            default='www-data',
            help='Apache group',
        ),
        optparse.make_option('--push',
            action='store_true',
            dest='awsoverwrite',
            help='Force over-write mode to remote aws instance',
        ),
        optparse.make_option('--reinstall',
            action='store_true',
            dest='awsreinstall',
            help='Force re-installation mode for remote aws python instance',
        ),
        optparse.make_option('--updateos',
            action='store_true',
            dest='updateos',
            help='Update the OS in the process',
        ),
        optparse.make_option('--updatepy',
            action='store_true',
            dest='updatepy',
            help='Update (reinstall) the python virtualenv',
        ),
        optparse.make_option('--noupdatepy',
            action='store_false',
            dest='updatepy',
            help='Do NOT update (reinstall) the python virtualenv',
        ),
        optparse.make_option('--restart',
            action='store_true',
            dest='restart',
            help='Restart the Apache service when finished',
        ),
        optparse.make_option('--reboot',
            action='store_true',
            dest='reboot',
            help='Reboot the server when finished',
        ),

        optparse.make_option('--fabricrc',
            action='store',
            type='string',
            dest='fabricrc',
            help='Settings file name'),

        )
    fab_api.env['unsaved'] = False

    #################################################################
    def handle(self, *args, **options):
        """
        Command argument processor
        """

        reboot=False
        restart=False

        # Parse the options and make any settings changes as needed
        if options.get('sitename', None):
            fab_api.env['SITENAME'] = options['sitename']
            fab_api.env['unsaved'] = True
        fab_api.env['rcfile'] = options.get('fabricrc', './.aws_fabric')

        ###TODO: this should be yanked and replaced with a boto config file solution instead
        rcfile = options.get('fabricrc', None)
        if rcfile:
            rcfile = os.path.abspath(rcfile)
        else:
            rcfile = os.path.abspath(os.path.join(os.getcwd(),'.aws_fabric'))

        fab_api.env['rcfile'] = rcfile

        ssh_pubkey_file = options.get('aws_security_key', None)

        # Load/set the settings
        self.set_awsSettings()

        # Parse the arguments
        if len(args)==0:
            self.get_awsInstanceList()
            #self.cmd_awsManage(args, options)
        else:
            if 'instance' in args:
                self.set_awsSSHKey()
                self.get_awsInstance()
            elif 'terminate' in args:
                self.cmd_terminateInstance()
            elif 'ip' in args:
                self.cmd_getIP()
            elif 'rmkey' in args:
                self.cmd_rmKey()
            elif 'addkey' in args:
                self.cmd_addKey(ssh_pubkey_file)
            elif 'keys' in args:
                self.cmd_listKeys()
            elif 'settings' in args:
                self.list_awsSettings()
            elif 'firewall' in args:
                self.set_awsSecurityGroups()
            elif 'create' in args:
                self.set_awsSSHKey(ssh_pubkey_file)
                self.set_awsSecurityGroups()
                self.install_awsUbuntuUpgrades()
                ###TODO: need to enable this as default, as soon as the function works safely
                #self.set_awsElasticIP()
                self.sync_awsProject(push=True)
                self.install_awsPythonRequirements(reinstall=True)
                self.aws_DropDB()
                self.sync_awsDB()
                self.sync_awsStaticfiles()
                self.set_awsPermissions()
                self.set_awsApacheconf(options.get('domain', None))
                reboot=True
            elif 'update' in args:
                if options.get('updateos', False):
                    self.install_awsUbuntuUpgrades()
                self.sync_awsProject(push=options.get('awsoverwrite', False))
                if options.get('updatepy', False):
                    self.install_awsPythonRequirements(reinstall=options.get('awsreinstall', False))
                #self.sync_awsPurify() #we would only need this if we were moving the database back and forth
                self.sync_awsDB()
                if options.get('updatepy', False):
                    self.sync_awsStaticfiles()
                self.set_awsPermissions()
            elif 'perms' in args:
                self.set_awsPermissions()
            elif 'apache' in args:
                self.set_awsApacheconf(options.get('domain', None))
            elif 'shell' in args:
                self.cmd_awsShell()
            elif 'dropdb' in args:
                self.aws_DropDB()
                self.sync_awsDB()
            if reboot or 'reboot' in args or options.get('reboot', False):
                self.cmd_awsReboot()
            elif restart or 'restart' in args or options.get('restart', False):
                self.sync_awsStaticfiles()
                self.set_awsPermissions()
                self.cmd_awsApacheRestart()

    #################################################################

    def set_awsSettings(self, path=None):
        """
        Load any settings found, or prompt for them.
        """

        if not path:
            # If path is not specified, use the default
            path = fab_api.env.rcfile

        if os.path.exists(path):
            # If the RC file exists, load it up
            comments = lambda s: s and not s.startswith("#")
            filesettings = filter(comments, open(path, 'r'))
            settings_dict = dict((k.strip(), v.strip()) for k, _, v in
                [s.partition('=') for s in filesettings])
            fab_api.env.update(settings_dict)

        # NOTE bugged me how the prompts where random, so i sorted them
        for key, prompt_pair in sorted(AWS_SETTINGS_PROMPTS.items(), key=lambda x: x[0]):
            question, default = prompt_pair
            # only save the setting to file if it exists and has a value
            # and allow for the fact that the instance may not exist yet.
            if not key in fab_api.env and not key == 'AWS_INSTANCE_ID':
                fab_api.prompt("%s :" % question, key, default)
                fab_api.env['unsaved'] = True

        fab_api.env['user'] = fab_api.env.AWS_USER

        self.save_awsSettings()

    def list_awsSettings(self):
        """
        Shows settings related to AWS actions
        """

        print("-"*55)
        print(fab_colors.yellow("AWS Instance Settings:"))
        print("-"*55)
        for setting in AWS_SETTINGS_PROMPTS:
            if setting in fab_api.env:
                if fab_api.env[setting]:
                    print("%55s : %-20s" % ( fab_colors.yellow(AWS_SETTINGS_PROMPTS[setting][0]), fab_colors.cyan( fab_api.env[setting])))
        print("-"*55)
        ###TODO: move all AWS settings to the boto config file, and site settings to settings.py - makes more sense that way
        #print BotoConfig.getboolean('Boto','debug')
        #print BotoConfig.get('Credentials','aws_access_key_id')


    def save_awsSettings(self, path=None):
        """
        Write the settings for AWS to file
        """
        if not path:
            path = fab_api.env.rcfile

        # Write these settings back to the fabric.env.rcfile only if needed
        if fab_api.env.get('unsaved', False):

            fab_api.env['unsaved'] = False
            print(fab_colors.green("Saving settings to %s." % path))

            local_settings_file = open(path, "w")
            local_settings_file.write("# This file was autocreated from Soupmix.\n")
            local_settings_file.write("# Do not edit this file directly, all changes will be lost!\n")
            for setting in AWS_SETTINGS_PROMPTS:
                if setting in fab_api.env:
                    value = fab_api.env[setting] or ''
                    if value:
                        local_settings_file.write("%s = %s\n" % (setting, value) )

            local_settings_file.close()


    def get_awsInstanceList(self):
        """
        Lists all AWS instances in the account
        """

        self.get_awsConnection()

        instance_list = []
        reservations = self.conn.get_all_instances()

        if reservations:
            for reservation in reservations:
                instances = reservation.instances
                for instance in instances:
                    print('%s) %s (%s-%s)\t%s (%s/%s/%s)\t%s (%s)' % (
                        fab_colors.yellow(len(instance_list)),
                        instance.id, instance.instance_type, instance.state,
                        instance.image_id, instance.region.name, instance.architecture, instance.root_device_type,
                        instance.public_dns_name, instance.ip_address,
                        ))
                    instance_list += [instance]
        else:
            print("No instances found.")

        return instance_list

    def get_awsInstance(self,create=True):
        """
        Gets or creates an instance for AWS actions
        """
        if not self.instance:

            self.get_awsConnection()

            if 'AWS_INSTANCE_ID' in fab_api.env:
                try:
                    self.instance = self.conn.get_all_instances(instance_ids=fab_api.env.AWS_INSTANCE_ID)[0].instances[0]
                except:
                    pass
                    # Ya know what? If it is a bad ID, then lets just offer to change it!  ;)

            # If no valid instance is pre-set then lets go get one!
            if not self.instance:
                # Show the existing instances
                instance_list = self.get_awsInstanceList()

                # If there are any, offer to select one
                if instance_list:
                    fab_api.prompt('Select an existing instance or hit enter to create a new one:', 'instance_selection')
                    if fab_api.env.instance_selection:
                        self.instance = instance_list[int(fab_api.env.instance_selection)]
                        fab_api.env['AWS_INSTANCE_ID'] = self.instance.id
                        print(fab_colors.green("%s selected." % (self.instance.id,)))
                        fab_api.env['unsaved'] = True

            # Nope.  No valid instance is selected, yet.  Time to create one then!
            if not self.instance and create:
                fab_api.warn('Creating new instance in the %s region with the %s image.' % (fab_api.env.AWS_REGION, fab_api.env.AWS_AMI_ID, ))

                (keyid, keyvalue) = self.get_sshKey()

                # Creates a server instance in your AWS account
                reservation = self.conn.run_instances(
                    image_id= fab_api.env.AWS_AMI_ID,
                    instance_type=fab_api.env.AWS_TYPE,
                    key_name=keyid,
                    security_groups=['apache', 'developer',],
                    )

                # Select the just-created instance
                self.instance = reservation.instances[0]
                fab_api.env['AWS_INSTANCE_ID'] = self.instance.id
                print(fab_colors.green("Server instance %s created." % (self.instance.id,)))
                fab_api.env['unsaved'] = True

                # Give the instance a head start getting spun-up
                sleep(60)


            # Write the instance data to the local settings
            self.save_awsSettings()

        # Make sure that the instance has spun-up before continuing
        while self.instance.state != 'running':
            print fab_colors.yellow("Waiting for instance...")
            sleep(5)
            self.instance.update()
            if self.instance.state == 'running':
                print fab_colors.green("Instance %s is up!" % self.instance.id)

        fab_api.env.host_string = self.instance.ip_address
        return self.instance


    def set_awsElasticIP(self):
        """
        """
        ###TODO: TEST THIS BEFORE USING!!!  ..and add some error catching fer crying out loud!
        ###TODO: check if there already is an elasticIP assigned to this instance before creating ANOTHER
        ###TODO: check to see if even though an EIP exists, whether this instance still needs it (use options?)

        instance = self.get_awsInstance()
        elasticip = self.conn.allocate_address()
        self.conn.associate_address(instance_id=instance.id , allocation_id=elasticip.allocation_id)


    def get_sshKey(self, keyfile=None):
        if not keyfile:
            home = os.getenv('USERPROFILE') or os.getenv('HOME')
            keyfile = os.path.abspath(os.path.join(home, ".ssh", "id_rsa.pub"))
        keyfile = os.path.expanduser(keyfile)
        try:
           kf = open(keyfile)
        except IOError as e:
            print fab_colors.red('Keyfile: %s does not exist!  Please specify a valid pubkey file with --sshpubkey=PATH_TO_SECURITY_KEY' % keyfile)
            sys.exit(0)
        keyvalue = kf.readline()
        keyid = keyvalue.split()[-1].strip() # delimeter not always "== ", but always id is last text following final space
        kf.close()

        return (keyid, keyvalue)

    def set_awsSSHKey(self, keyfile=None):
        """
        Imports your local ssh pubkey into your AWS account
        """

        try:
            (keyid, keyvalue) = self.get_sshKey(keyfile)
        except:
            raise Exception("SSH pubkey not found! Cannot continue!")


        self.get_awsConnection()

        # Import a security pub key for us to use ssh with
        try:
            # Look to see if it already exists first
            keypairs = self.conn.get_all_key_pairs(keynames=[keyid,])
        except BotoException.EC2ResponseError:
            # Nope.  Not there!  Lets create it
            self.conn.import_key_pair(keyid,keyvalue)
            print(fab_colors.green("Key ID '%s' installed from %s." % (keyid, keyfile)))
        else:
            print(fab_colors.green("Key ID '%s' exists." % keyid))

    def set_awsSecurityGroups(self):
        """
        Creates necessary firewall security groups in your AWS account
        """

        self.get_awsConnection()

        # Check security group for the webserver
        try:
            self.conn.get_all_security_groups(groupnames=['apache',])
        except BotoException.EC2ResponseError:
            # Create a security group for internet access to the webserver
            web = self.conn.create_security_group('apache', 'Apache Security Group')
            web.authorize('tcp', 80, 80, '0.0.0.0/0')
            print(fab_colors.green("Apache firewall entry added."))
        else:
            print(fab_colors.green("Apache firewall entry exists."))

        # Check security group for the developer access
        try:
            self.conn.get_all_security_groups(groupnames=['developer',])
        except BotoException.EC2ResponseError:
            # Create a security group for internet access to the test server and ssh
            dev = self.conn.create_security_group('developer', 'Developer Security Group')
            dev.authorize('tcp', 8000, 8000, '0.0.0.0/0')
            dev.authorize('tcp', 22, 22, '0.0.0.0/0')
            print(fab_colors.green("Developer firewall entry added."))
        else:
            print(fab_colors.green("Developer firewall entry exists."))

    def install_awsUbuntuUpgrades(self):
        """
        Installs the core components needed to run Django, Apache etc on Ubuntu
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address
        fab_api.env.key_filename = '~/.ssh/id_rsa'


        # Update all of the server and library components first
        print(fab_colors.yellow("Checking OS for available updates..."))
        fab_api.sudo('apt-get -y update')
        fab_api.sudo('apt-get -y dist-upgrade')

        # Install all of the server and library components
        print(fab_colors.yellow("Checking OS for required packages..."))
        fab_api.sudo('apt-get -y install python-setuptools python-dev python-virtualenv git mercurial gcc unison python-pip node-less libtidy-dev')

        # Install Apache and necesary components
        fab_api.sudo('apt-get -y install apache2 libapache2-mod-wsgi')

        # Install PIL support for Virtual Environment on 64 bit systems
        fab_api.sudo('apt-get -y install python-imaging libjpeg62 libjpeg62-dev libjpeg8')

        # Link the libraries so that PIL can find them
        if not fab_exists('/usr/lib/libz.so'):
            fab_api.sudo('ln -s  /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/')
        if not fab_exists('/usr/lib/libjpeg.so'):
            fab_api.sudo('ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/')

        # Instal MySQL components to system
        fab_api.sudo('apt-get install -y mysql-server mysql-client python-mysqldb libmysqlclient-dev build-essential python-dev')
        fab_api.sudo('apt-get -y install python-mysqldb')

        # Clean up our mess and reduce system footprint on the HDD
        fab_api.sudo('apt-get -y clean')


        # Create the base directory
        ###TODO: make this use a dynamic variable instead of hardcoded as it is
        if not fab_exists('/home/ubuntu/django'):
            fab_api.run('mkdir /home/ubuntu/django')
        if not fab_exists('/home/ubuntu/django/cache'):
            fab_api.run('mkdir /home/ubuntu/django/cache')


    def cmd_awsReboot(self):
        """
        Reboot the AWS server
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        print fab_colors.yellow("Rebooting instance...")
        fab_api.sudo('reboot')
        sleep(60)
        while self.instance.state != 'running':
            print fab_colors.yellow(self.instance.state)
            sleep(5)
            self.instance.update()

    def aws_DropDB(self):
        """
        Drop the database and recreate
        """
        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        fab_api.prompt('What is the server MySQL root password:', 'mysqlpwd')
        fab_api.run('mysql -u root -p%s -e "DROP DATABASE IF EXISTS django_%s;"' % (fab_api.env.mysqlpwd, fab_api.env.SITENAME))
        fab_api.run('mysql -u root -p%s -e "CREATE DATABASE django_%s;"' % (fab_api.env.mysqlpwd, fab_api.env.SITENAME))
        fab_api.run('mysql -u root -p%s -e "GRANT ALL ON django_%s.* TO \'djangouser\'@\'localhost\' IDENTIFIED BY \'%s\';"' % (fab_api.env.mysqlpwd, fab_api.env.SITENAME, fab_api.env.mysqlpwd))

    def install_awsPythonRequirements(self, reinstall=False):
        """
        Installs the Python virtual environment needed for safe-n-sane Django using the
        requirements.txt file contents
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        print(fab_colors.yellow("Updating Python virtual environment (this may take around 20 minutes the first time)..."))

        if reinstall:
            ###TODO: create a dated and sorted freeze first
            print(fab_colors.yellow("Creating Python virtual environment..."))
            fab_api.run('rm -rf ~/django/python')
            fab_api.run('virtualenv --no-site-packages --distribute ~/django/python')

        with fab_api.settings(
                            fab_api.cd('~/django/%s' % fab_api.env.SITENAME),
                            fab_api.prefix('source ~/django/python/bin/activate')):

            # Install MySQL-Python with appropriate distribute version as well
            fab_api.run('pip install --upgrade --download-cache=/home/ubuntu/django/cache --source=/home/ubuntu/django/cache distribute==0.6.30')
            fab_api.run('pip install --upgrade --download-cache=/home/ubuntu/django/cache --source=/home/ubuntu/django/cache MySQL-python==1.2.3')

            # Install all of the modules in requirements.txt for this project
            fab_api.run('pip install --upgrade --download-cache=~/django/cache --source=~/django/cache -r requirements.txt')

    def sync_awsProject(self, push=False):
        """
        Sync the local copy up to the remote server
        """

        instance = self.get_awsInstance()

        ###TODO: Add -ignore flags for unison call

        here = os.getcwd()
        there = "ssh://ubuntu@%s//home/ubuntu/django/%s" % (instance.ip_address ,fab_api.env.SITENAME)

        print(fab_colors.yellow("Synchronizing project files..."))

        with fab_api.settings(warn_only=True): # unison has return code 1 when no changes
            if push:
                fab_api.local('unison -ignore "Path httpdocs"  -silent -force %s %s %s' % (here, here, there))
            else:
                fab_api.local('unison -auto -ignore "Path httpdocs"  %s %s' % (here, there))

    def sync_awsPurify(self):
        """
        Clear the menu cache or errors may ensue!
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        print(fab_colors.yellow("Cleaning menu entries..."))

        with fab_api.settings(
                            fab_api.cd('~/django/%s' % fab_api.env.SITENAME),
                            fab_api.prefix('source ~/django/python/bin/activate')):
            fab_api.run('python manage.py reset --noinput menus')


    def sync_awsDB(self, push=False):
        """
        Run the django database maintenance commands within the AWS server instance
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        print(fab_colors.yellow("Initializing/updating database..."))

        with fab_api.settings(
                            fab_api.cd('~/django/%s' % fab_api.env.SITENAME),
                            fab_api.prefix('source ~/django/python/bin/activate')):

            # Update the database and link all media files
            fab_api.run('python manage.py syncdb --noinput --verbosity=0')
            fab_api.run('python manage.py migrate --verbosity=0')


    def sync_awsStaticfiles(self):
        """
        Link the static files from the various modules into a common file tree for serving up on Apache
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        print(fab_colors.yellow("Collecting static files from included modules..."))

        with fab_api.settings(
                            fab_api.cd('~/django/%s' % fab_api.env.SITENAME),
                            fab_api.prefix('source ~/django/python/bin/activate')):

            # Link the media files

            if fab_exists('~/django/%s/httpdocs' % fab_api.env.SITENAME):
                fab_api.sudo('rm -rf ~/django/%s/httpdocs' % fab_api.env.SITENAME)
            fab_api.run('python manage.py collectstatic -l --noinput --verbosity=0')

    def set_awsApacheconf(self, domain=None):
        """
        Enable the Apache config
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        if not domain:
            fab_api.prompt('Base domain to host as:', 'domain', fab_api.env.SITENAME + ".com")
        else:
            fab_api['domain']=domain

        fab_api.env['django_base_dir'] = "/home/%s/django/" % fab_api.env.AWS_USER

        print(fab_colors.yellow("Creating and installing Apache configuration file..."))

        # upload the settings.py and apache config templates to project/website
        target = "/etc/apache2/sites-available/%s.conf" % fab_api.env.domain
        template = os.path.join('etc','apache2_vhost.conf')
        fab_op.put(template, target, use_sudo=True)

        if fab_exists('/etc/apache2/sites-enabled/000-default'):
            fab_api.prompt('Disable 000-default? (y/n) ', 'nopchdflt')
            if fab_api.env.nopchdflt == 'y':
                fab_api.sudo('a2dissite 000-default')

        fab_api.sudo('a2ensite %s.conf' % fab_api.env.domain)

    def cmd_awsApacheRestart(self):
        """
        Restart Apache
        """
        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        print(fab_colors.yellow("Reloding Apache..."))

        fab_api.sudo('/etc/init.d/apache2 reload')

    def cmd_terminateInstance(self):
        """terminate instance and remove from .aws_fabric"""
        instance = self.get_awsInstance()
        print fab_colors.red('You are about to TERMINATE an instance. This CANNOT be undone.')
        print fab_colors.red('!!!!!!!!!! You will LOSE all its DATA. !!!!!!!!!!!!!!!!!!!!!!!')
        print 'id: %s ip_address: %s' % (instance.id, instance.ip_address)
        output = raw_input('\nTo proceed, type the ip address of this instance: ')
        # terminate instance
        if output == instance.ip_address:
            instance.terminate()
        # remove instance from .aws_fabric
        path = fab_api.env.get('rcfile')
        if isfile(path):
            with open(path) as file:
                new_lines = [line for line in file if 'AWS_INSTANCE_ID' not in line]
            with open(path,'w') as file:
                file.writelines(new_lines)
        print fab_colors.yellow('\ninstance terminated')

    def _list_keys_on_remote(self, id_only=False):
        """get ssh keys on remote"""
        with fab_api.hide('everything'):
            output = fab_api.run('cat ~/.ssh/authorized_keys')
        if id_only:
            return [line.split()[-1] for line in output.splitlines()]
        else:
            return output.splitlines()

    def cmd_rmKey(self):
        """rm keys from remote"""
        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address
        ids = self._list_keys_on_remote(id_only=True)

        def prompt_for_delete(): # local func so it can easily be repeated
            print fab_colors.yellow("\n========================\nThese keys are installed.")
            for num, id in enumerate(ids):
                print '(%s) %s' % (num, id)
            print fab_colors.yellow('\nEnter the numbers of the keys to delete, seperated by spaces.')
            # get keys to delete
            input = raw_input('nums: ')
            to_delete = [int(num) for num in input.split() if num.isdigit()]
            to_delete = filter(lambda x: 0 <= x < len(ids), to_delete)
            # validate selection, to prevent terrible crisis
            if not to_delete:
                print fab_colors.red('\nYou didnt choose anything. Lets start over...')
                prompt_for_delete()
            if len(to_delete) >= len(ids):
                print fab_colors.red('\nDO NOT delete all keys. you will be LOCKED OUT permanently.')
                prompt_for_delete()
            key_id, key_value = self.get_sshKey()
            if ['fail' for num in to_delete if ids[num]==key_id ]:
                print fab_colors.red('\nDUDE. Do NOT delete you own key. Get a grip...')
                prompt_for_delete()
            # print selection and confirm
            print fab_colors.yellow('\nYou would like to delete:')
            for num in sorted(to_delete):
                print '(%s) %s' % (num, ids[num])
            output = raw_input('\nIs this correct? ' + fab_colors.yellow('[yes|no]') + ' : ')
            # update the keys
            if output == 'yes':
                old_keys = enumerate(self._list_keys_on_remote())
                new_keys = [key for num, key in old_keys if num not in to_delete]
                new_keys =  '\n'.join(new_keys)
                with fab_api.hide('everything'):
                    fab_api.run('echo "%s" > ~/.ssh/authorized_keys' % new_keys)
                to_print =  fab_colors.yellow('\ndeleted keys ')
                to_print += fab_colors.yellow(' and ').join([ids[num] for num in to_delete])
                to_print += fab_colors.yellow(' from remote.')
                print to_print
            # if chose not to proceed, start over
            else:
                prompt_for_delete()

        prompt_for_delete() # call the func

    def cmd_addKey(self, keyfile=None):
        """
        add keys to remote
        """
        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address
        print(fab_colors.yellow("Enter ssh pub keys, one per line.\nEnter blank line to terminate input."))
        # prompt for ssh keys
        keys = []
        while True:
            output = raw_input('ssh pub key: ')
            if output:
                keys.append(output)
            else:
                break
        # add keys to remote
        for key in keys:
            with fab_api.hide('everything'):
                fab_api.run('echo "%s" >> ~/.ssh/authorized_keys' % key)
        print(fab_colors.yellow("keys have been added to remote instance."))

    def cmd_listKeys(self):
        """list the id/user of all installed ssh keys on remote instance"""
        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address
        print(fab_colors.yellow("Pub Key IDs..."))
        print '\n'.join(self._list_keys_on_remote(id_only=True))

    def cmd_getIP(self):
        """print the ip of our instance"""
        instance = self.get_awsInstance(create=False)
        if instance:
            print instance.ip_address
        else:
            print 'no instance created yet'

    def cmd_awsShell(self):
        """
        Open an interactive shell on the AWS server instance
        """
        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address
        fab_api.open_shell()


    #noinspection PyUnusedLocal
    def cmd_awsManage(self, *args, **options):
        """
        Run any series of available Django command in the aws instance
        """
        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        ###TODO: Clean this up so that it accepts options like the local command does

        with fab_api.settings(
                            fab_api.cd('~/django/%s' % fab_api.env.SITENAME),
                            fab_api.prefix('source ~/django/python/bin/activate')):

            for cmd in args[0]:
                fab_api.run(command='python manage.py %s' % cmd)
                #print('python manage.py %s' % cmd)


    def set_awsPermissions(self):
        """
        Set file permissions to usable values
        """

        instance = self.get_awsInstance()
        fab_api.env.host_string = instance.ip_address

        print(fab_colors.yellow("Settings apropriate default permissions on project files..."))

        fab_api.sudo('chown -R %s:%s ~/django/%s/%s/static' % (fab_api.env.AWS_USER, fab_api.env.AWS_HTTPD_GROUP, fab_api.env.SITENAME, fab_api.env.SITENAME))
        fab_api.sudo('chmod -R ug+rw ~/django/%s/%s/static' % (fab_api.env.SITENAME, fab_api.env.SITENAME))

        # Add access to the webserver to write into the cache directory
        fab_api.sudo('chown -R %s:%s ~/django/%s/' % (fab_api.env.AWS_USER, fab_api.env.AWS_HTTPD_GROUP, fab_api.env.SITENAME))
        fab_api.sudo('chmod -R ug+rw ~/django/%s/' % (fab_api.env.SITENAME))


    def get_awsConnection(self):
        """
        Get or create the connection object to AWS
        """

        if self.conn:
            return self.conn

        # Create a connection to the AWS region of choice with our keys
        self.conn = ec2.connect_to_region(
            region_name             = fab_api.env.AWS_REGION,
            aws_access_key_id       = fab_api.env.AWS_ACCESS_KEY_ID,
            aws_secret_access_key   = fab_api.env.AWS_ACCESS_SECRET,
            )

        if not self.conn:
            raise Exception("No AWS Connection! Cannot continue!")

        return self.conn

class RESTRequest(Request):
    def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None):
        Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
        self.method = method

    def get_method(self):
        if self.method:
            return self.method
        return Request.get_method(self)

class DeployKey():

    def __init__(self, spice_repo=None, repo_owner=None, owner_passwd=None):
        self.spice_repo = spice_repo
        self.repo_owner = repo_owner
        self.owner_passwd = owner_passwd
        #if owner is None:
            #print "What would you like to do?"
            #print ""
            #print "(g)et a listing of a repositories deploy keys"
            #print "(a)uthorize a deploy key with BitBucket"
            #print "(d)eauthorize a deploy key with BitBucket"
            #print ""
            #reply = raw_input("[")
            #if reply == "g":
                #pass
                ##add definition for owner,owner_passwd,spice_repo cli
                ##self.getKeys()
            #elif reply == "a":
                #pass
                ##self.postKey(ssh_key,key_label)
            #elif reply == "d":
                #pass
                ##add addition prompt for ssh keyid preceded by readout of key choices by 'label' and 'ak'
                ##readout via 'for item in' sort of thing....?
                ##self.delKey()
            #else:
                #return False

    def decode_list(self, jsonData):
        rv = []
        for item in jsonData:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self.decode_list(item)
            elif isinstance(item, dict):
                item = self.decode_dict(item)
            rv.append(item)
        return rv

    def decode_dict(self, jsonData):
        rv = {}
        for key, value in jsonData.iteritems():
            if isinstance(key, unicode):
               key = key.encode('utf-8')
            if isinstance(value, unicode):
               value = value.encode('utf-8')
            elif isinstance(value, list):
               value = self.decode_list(value)
            elif isinstance(value, dict):
               value = self.decode_dict(value)
            rv[key] = value
        return rv

    def getCred(self):
        credentials = b64encode("{0}:{1}".format(self.owner, self.owner_passwd).encode()).decode("ascii")
        return credentials

    def getURL(self):
        url = "https://api.bitbucket.org/1.0/repositories/%s/%s/deploy-keys" % (self.owner, self.spice_repo)
        return url

    def getHeaders(self):
        headers = {'Authorization': "Basic " + self.getCred()}
        return headers

    def getKeys(self):
        request = RESTRequest(url=self.getURL(), headers=self.getHeaders(), method="GET")
        connection = urlopen(request)
        content = connection.read()
        return json.loads(content, object_hook=self.decode_dict)

    def postKey(self,ssh_key,key_label):
        data = urlencode({"key": ssh_key, "label": key_label})
        request = RESTRequest(url=self.getURL(), headers=self.getHeaders(), data=data, method="POST")
        connection = urlopen(request)
        connection.read()

    def delKey(self,key_id):
        request = RESTRequest(url="%s/%s" % (self.getURL(), key_id), headers=self.getHeaders(), method="DELETE")
        connection = urlopen(request)
        connection.read()
