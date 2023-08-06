"""
    All Crawley's commands must be here
"""

from crawley.utils import exit_with_error

from run import RunCommand
from shell import ShellCommand
from startproject import StartProjectCommand
from syncdb import SyncDbCommand
from migratedb import MigrateDbCommand
from browser import BrowserCommand

class CommandsDict(dict):

    def __getitem__(self, key):

        if key in self:
            return dict.__getitem__(self, key)
        else:
            exit_with_error("[%s] Subcommand not valid" % (key))


commands = CommandsDict()

d = { RunCommand.name : RunCommand,
      ShellCommand.name : ShellCommand,
      StartProjectCommand.name : StartProjectCommand,
      SyncDbCommand.name : SyncDbCommand,
      BrowserCommand.name : BrowserCommand,
      MigrateDbCommand.name : MigrateDbCommand }

commands.update(d)

