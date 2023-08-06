'''
Usage:
pyb-init local
pyb-init github <user> : <project>

-h --help    show this
'''
from __future__ import absolute_import
__version__ = '0.1.0'

from docopt import docopt
from pyb_init import reactor


def entry_point():
    parsed_command_line = docopt(doc=__doc__, version=__version__)
    task_reactor = None
    if parsed_command_line['local']:
        task_reactor = reactor.for_local_initialization()
    if parsed_command_line['github']:
        task_reactor = reactor.for_github_clone(user=parsed_command_line['<user>'],
                                                project=parsed_command_line['<project>'])

    for task in task_reactor.get_tasks():
        task.execute()
