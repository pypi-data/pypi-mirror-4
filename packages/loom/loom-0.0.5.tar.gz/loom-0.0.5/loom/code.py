from fabric.api import task, run, sudo
from fabric.contrib.project import rsync_project

@task
def upload():
    run('mkdir -p ~/code')
    sudo('chown ubuntu:ubuntu ~/code') # ???
    rsync_project(
        local_dir="code/",
        remote_dir="~/code",
        delete=True,
        extra_opts='--exclude=".git*"',
        ssh_opts='-oStrictHostKeyChecking=no'
    )


