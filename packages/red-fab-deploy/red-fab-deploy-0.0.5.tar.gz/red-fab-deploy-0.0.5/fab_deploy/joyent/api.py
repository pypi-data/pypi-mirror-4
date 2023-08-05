import sys
import time

from fabric.api import env, execute
from fabric.tasks import Task

from fab_deploy import functions

from smartdc import DataCenter

DEFAULT_PACKAGE = 'Small 1GB'
DEFAULT_DATASET = 'smartos64'

class New(Task):
    """
    Provisions and sets up a new joyent server.

    Uses the joyent API for provisioning a new server. In order
    to run this task your fabfile must contain a line like:

    ``joyent_account = 'account_name'``

    Takes the following arguments:

    * **dataset**: The name of the joyent data set you want to use.
             Defaults to Small 1GB.

    * **server_size**: The size server you want. Defaults to smartos64.

    * **type**: Required. The type of server you are provisioning. This
          should correspond to a setup task. If no such task is
          found an error will be raised.

    * **data_center**: The datacenter to provision this server in.
                 If not provided your env will be checked for
                 joyent_default_data_center if that does not exist
                 either an error will be raised.

    You will be prompted to enter your ssh key name, this should correspond
    with the name that was used when your key was registered with this joyent
    account.

    Once your machine is provisioned and ready (this can take up to 10 mins).
    The setup task you provided will be run.

    Please note that care should be taken when running this command to make
    sure that too many machines are not created. If an error occurs while
    waiting for the machine to be ready or while running the setup task
    this command should not be run again or another machine will be provisioned.
    Rememeber setup tasks can be executed directly.

    This is a serial task and should not be called with any hosts
    as the provisioned server ends up being the remote host.
    """

    name = 'add_server'
    serial = True

    def run(self, **kwargs):
        """
        """
        assert not env.hosts
        if not env.get('joyent_account'):
            print "To use the joyent api you must add a joyent_account value to your env"
            sys.exit(1)

        setup_name = 'setup.%s' % kwargs.get('type')

        task = functions.get_task_instance(setup_name)

        default_dataset = DEFAULT_DATASET
        default_package = DEFAULT_PACKAGE

        if task:
            if hasattr(task, 'dataset'):
                default_dataset = task.dataset
            if hasattr(task, 'server_size'):
                default_package = task.server_size
        else:
            print "I don't know how to add a %s server" % kwargs.get('type')
            sys.exit(1)

        location = kwargs.get('data_center')
        if not location and env.get('joyent_default_data_center'):
            location = env.joyent_default_data_center
        elif not location:
            print "You must supply an data_center argument or add a joyent_default_data_center attribute to your env"
            sys.exit(1)

        key_name = raw_input('Enter your ssh key name: ')
        key_id = '/%s/keys/%s' % ( env.joyent_account, key_name)
        sdc = DataCenter(location=location, key_id=key_id)

        name = functions.get_remote_name(None, task.config_section,
                                         name=kwargs.get('name'))
        new_args = {
            'name' : name,
            'dataset' : kwargs.get('data_set', default_dataset),
            'metadata' : kwargs.get('metadata', {}),
            'tags' : kwargs.get('tags', {}),
            'package' : kwargs.get('package', default_package)
        }

        machine = sdc.create_machine(**new_args)

        public_ip = machine.public_ips[0]
        print "added machine %s" % public_ip
        host_string = 'admin@%s' % public_ip

        print "waiting for machine to be ready"
        while machine.status() != 'running':
            print '.'
            time.sleep(5)
        print 'done'

        execute(setup_name, name=name, hosts=[host_string])

add_server = New()
