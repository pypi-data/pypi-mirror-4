import boto
from fabric.api import *
import re
import socket
import time
import boto.exception
import os

# Security group. Automatically created if it doesn't exist.
env.ec2_security_group = 'loom'

# Default EC2 region
env.ec2_region = "us-east-1"

# Default AMI
# us-east-1 precise amd64 ebs
env.ec2_ami = 'ami-a29943cb'

# Default instance type
env.ec2_instance_type = 't1.micro'

# Default keypair
env.key_filename = 'loom.pem' 

conn = boto.connect_ec2()

def configure():
    # Fill roledefs with hosts from EC2
    for instance in get_instances(environment=env.environment):
        name = get_name(instance)
        if name['role'] not in env.roledefs:
            env.roledefs[name['role']] = []
        env.roledefs[name['role']].append(instance.ip_address)

@task
def create(role):
    """
    Creates an instance of a given role.
    """

    name = get_next_name(env.environment, role)
    puts('Creating "%s"...' % name)

    key_pair_name = create_key_pair()
    security_group = create_security_group()

    reservation = conn.run_instances(
        env.ec2_ami,
        key_name=key_pair_name, 
        instance_type=env.ec2_instance_type,
        security_groups=[security_group],
    )
    instance = reservation.instances[0]
    # TODO: instance may not exist at this point, got InvalidInstanceID.NotFound
    instance.add_tag('Name', name)

    puts('Waiting for server to start...')
    while instance.state != 'running':
        time.sleep(0.5)
        instance.update()

    # wait for server to come up
    puts('Waiting for SSH to come up on %s...' % instance.ip_address)
    s = socket.socket()
    while True:
        try:
            s.connect((instance.ip_address, 22)) 
        except Exception, e:
            time.sleep(0.25)
        else:
            break

    time.sleep(1)

    # Update state for subsequent tasks
    env.hosts.append(instance.ip_address)
    env.roledefs[role].append(instance.ip_address)

    sudo('apt-get update')

    if role == 'puppetmaster':
        execute(puppet.install_master)
    else:
        execute(puppet.install_agent)

@runs_once
@task
def create_all():
    """
    Creates instances for roles which do not exist yet.
    """
    instances = get_instances(environment=env.environment)
    existing_roles = [get_name(i)['role'] for i in instances if get_name(i)]
    for role in env.roledefs:
        if role not in existing_roles:
            create(role)

def create_key_pair():
    key_pair_name = re.sub(r'\.pem$', '', os.path.basename(env.key_filename))
    key_pair = conn.get_key_pair(key_pair_name)
    if key_pair is None:
        puts('Creating key pair "%s"' % key_pair_name)
        key_pair = conn.create_key_pair(key_pair_name)
        key_pair.save(os.path.dirname(env.key_filename))
    return key_pair_name

def create_security_group():
    try:
        conn.get_all_security_groups(env.ec2_security_group)
    except boto.exception.EC2ResponseError:
        puts('Creating %s security group' % env.ec2_security_group)
        conn.create_security_group(env.ec2_security_group, 'default security group')
        for port in [22, 80]:
            conn.authorize_security_group(
                env.ec2_security_group,
                ip_protocol = 'tcp',
                from_port = port,
                to_port = port,
                cidr_ip = '0.0.0.0/0',
            )
    return env.ec2_security_group

def get_next_name(environment, role):
    max_id = 0
    for instance in get_instances(state=None, environment=environment, role=role):
        name = get_name(instance)
        if name['identifier'] > max_id:
            max_id = name['identifier']
    return '%s-%s-%s' % (environment, role, max_id + 1)

def get_name(instance):
    try:
        tag_value = instance.tags['Name']
    except KeyError:
        return
    return parse_name(tag_value)

def parse_name(name):
    try:
        bits = name.split('-', 3)
        return {
            'environment': bits[0],
            'role': bits[1],
            'identifier': int(bits[2]),
        }
    except (IndexError, ValueError):
        return None

def get_instances(state='running', environment=None, role=None):
    filters = {}
    if state:
        filters['instance-state-name'] = state
    reservations = conn.get_all_instances(filters=filters)
    instances = []
    for reservation in reservations:
        for instance in reservation.instances:
            name = get_name(instance)
            if not name:
                continue
            if environment is not None and name['environment'] != environment:
                continue
            if role is not None and name['role'] != role:
                continue
            instances.append(instance)
    return instances

@task
def describe():
    try:
        import termcolor
        has_termcolor = True
    except ImportError:
        has_termcolor = False

    instances_by_role = {}
    for instance in get_instances():
        role = get_name(instance)['role']
        if role in instances_by_role:
            instances_by_role[role].append(instance)
        else:
            instances_by_role[role] = [instance]

    for role, instances in instances_by_role.iteritems():
        if has_termcolor:
            termcolor.cprint(role + ':', attrs = ['bold'])
        else:
            print(role + ':')
        for instance in instances:
            print('  %-15s (%s)' % (instance.ip_address, instance.instance_type))
        print('')


