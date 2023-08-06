import sys
import os
import logging
logger = logging.getLogger('snaptastic.cli')

path = os.path.abspath(__file__)
parent = os.path.join(path, '../', '../')
sys.path.append(parent)

from argh import command, ArghParser
from snaptastic import get_snapshotter
from snaptastic import settings
import json


def configure_snapshotter(snapshotter_name, userdata=None):
    snapshotter_class = get_snapshotter(snapshotter_name)
    if userdata:
        userdata = json.loads(userdata)
    snap = snapshotter_class(userdata=userdata)
    return snap


def congfigure_log_level(level):
    '''
    Setup the root log level to the level specified in the string loglevel
    '''
    from snaptastic import settings
    level_object = getattr(logging, level)
    root_logger = logging.getLogger()
    root_logger.setLevel(level_object)

    snaptastic_logger = logging.getLogger('snaptastic')
    handlers = snaptastic_logger.handlers
    for handler in handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(level_object)
    # This is a bit of hack but we can only log about this after logging has been
    # properly setup :)
    logger.info('found settings at %s', settings.SETTINGS_MODULE)


@command
def make_snapshots(snapshotter_name, userdata=None, loglevel='DEBUG'):
    congfigure_log_level(loglevel)
    snap = configure_snapshotter(snapshotter_name, userdata)
    snap.make_snapshots()


@command
def mount_snapshots(snapshotter_name, userdata=None, loglevel='DEBUG',
                    ignore_mounted=False):
    congfigure_log_level(loglevel)
    snap = configure_snapshotter(snapshotter_name, userdata)
    snap.mount_snapshots(ignore_mounted=ignore_mounted)


@command
def unmount_snapshots(snapshotter_name, userdata=None, loglevel='DEBUG'):
    congfigure_log_level(loglevel)
    unmount = raw_input("Are you sure you want to unmount?: ")
    if unmount in ['y', 'yeay', 'yes']:
        snap = configure_snapshotter(snapshotter_name, userdata)
        snap.unmount_snapshots()


@command
def list_volumes(snapshotter_name, userdata=None, loglevel='DEBUG'):
    congfigure_log_level(loglevel)
    snap = configure_snapshotter(snapshotter_name, userdata)
    volumes = snap.get_volumes()
    for volume in volumes:
        print volume


@command
def clean(component, userdata=None, force=False, loglevel='DEBUG'):
    congfigure_log_level(loglevel)
    from snaptastic.cleaner import Cleaner
    run = True
    if not force:
        clean = raw_input("Are you sure you want to clean?(y,yeay,yes): ")
        run = clean in ['y', 'yeay', 'yes']
    if run:
        cleaner = Cleaner()
        cleaner.clean(component)


@command
def test(loglevel='DEBUG'):
    from snaptastic.utils import get_userdata_dict
    logger.info('trying to get userdata, requires boto and valid keys')
    try:
        userdata = get_userdata_dict()
        logger.info('found userdata, so that works %s', userdata)
    except Exception, e:
        logger.exception('Userdata lookup doesnt work, error %s', e)
    logger.info('next up instance metadata')
    from boto.utils import get_instance_metadata
    try:
        metadata = get_instance_metadata()
        logger.info('found instance metadata %s', metadata)
    except Exception, e:
        logger.exception('Metadata lookup doesnt work, error %s', e)


def main():
    from snaptastic import __version__
    if '--version' in sys.argv:
        print 'Snaptastic version %s' % __version__

    p = ArghParser()
    commands = [make_snapshots, mount_snapshots,
                list_volumes, unmount_snapshots, clean, test]
    p.add_commands(commands)
    p.dispatch()


if __name__ == '__main__':
    main()
