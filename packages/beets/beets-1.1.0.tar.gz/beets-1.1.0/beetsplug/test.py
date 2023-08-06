from __future__ import print_function

from beets.plugins import BeetsPlugin
from beets import ui

class TestPlugin(BeetsPlugin):
    def commands(self):
        def func(lib, opts, args):
            for item in lib.items():
                print(item.flexattrs['foo'].get('bar'))
                item.flexattrs['foo']['bar'] = args[0]
                lib.store(item)
        test_cmd = ui.Subcommand('test', help='test')
        test_cmd.func = func
        return [test_cmd]
