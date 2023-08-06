from . import meta
from . import string

class Command(object):
	"""
	A general-purpose base class for creating commands for a command-line
	program using argparse. Each subclass of Command represents a separate
	sub-command of a program.

	For example, one might use Command subclasses to implement the Mercurial
	command set::

		class Commit(Command):
			@staticmethod
			def add_arguments(cls, parser):
				parser.add_argument('-m', '--message')

			@classmethod
			def run(cls, args):
				"Run the 'commit' command with args (parsed)"

		class Merge(Command): pass
		class Pull(Command): pass
		...

	Then one could create an entry point for Mercurial like so::

		def hg_command():
			parser = argparse.ArgumentParser()
			Command.add_subparsers(parser)
			args = parser.parse_args()
			args.action.run()
	"""
	__metaclass__ = meta.LeafClassesMeta

	@classmethod
	def add_subparsers(cls, parser):
		subparsers = parser.add_subparsers()
		[cmd_class.add_parser(subparsers) for cmd_class in cls._leaf_classes]

	@classmethod
	def add_parser(cls, subparsers):
		cmd_string = string.words(cls.__name__).lowered().dash_separated()
		parser = subparsers.add_parser(cmd_string)
		parser.set_defaults(action=cls)
		return parser

	@classmethod
	def add_arguments(cls, parser):
		pass
