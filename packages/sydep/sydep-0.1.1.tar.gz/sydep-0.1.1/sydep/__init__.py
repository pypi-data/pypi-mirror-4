import os
import shutil

from ConfigParser import SafeConfigParser

PATH_PACKAGE = os.path.dirname(__file__)
FILE_CONFIG_SAMPLE = os.path.join(PATH_PACKAGE, 'sydep.cfg.sample')


def main(args):
    """
    Init function of script. Called by :file:`sydep`.

    :param args: dictionary of arguments from command \
                 line (got by :py:class:`docopt`)
    """
    if args['init']:
        copy_config()
    else:
        config = load_config()

        if args['push']:
            push(config, args)
        if args['pull']:
            pull(config, args)


def copy_config():
    """
    Copy sample config file into current directory.
    """
    try:
        open('./sydep.cfg', 'r')
        print 'Remove sydep.cfg first. It cannot be overwritten.'
    except:
        shutil.copyfile(FILE_CONFIG_SAMPLE, './sydep.cfg')


def load_config():
    """
    Load config from current directory.
    """
    file = open('./sydep.cfg', 'r')
    config = SafeConfigParser()
    config.readfp(file)
    return config


def push(config, args):
    """
    Push local files to remote server

    :param config: instance of :py:class:`ConfigParser`
    :param args: dictionary of arguments from command \
                 line (got by :py:class:`docopt`)
    """
    run_cmd('rsync -a{verbose}z --exclude-from=.sydepignore'
            ' -e ssh {local} {server}:{remote}', config, args)


def pull(config, args):
    """
    Update local files from server - overwrite just existing files,
    don't create new ones.

    :param config: instance of :py:class:`ConfigParser`
    :param args: dictionary of arguments from command \
                 line (got by :py:class:`docopt`)
    """
    run_cmd('rsync -a{verbose}z --existing --exclude-from=.sydepignore'
            ' -e ssh {server}:{remote} {local}', config, args)


def run_cmd(cmd, config, args):
    """
    Run given command after inserting variables.

    :param cmd: input command
    :param config: instance of :py:class:`ConfigParser`
    :param args: dictionary of arguments from command \
                 line (got by :py:class:`docopt`)
    """
    cmd = cmd.format(
        verbose='v' if not args['--quiet'] else '',
        server=config.get('server', 'server'),
        remote=config.get('server', 'remote'),
        local=config.get('server', 'local'),
    )

    if not args['--quiet']:
        print cmd

    os.system(cmd)
