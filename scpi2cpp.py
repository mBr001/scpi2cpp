#!python3

import os.path
from string import Template


class SCPISpecification:
	class SCPI_cmd:
		"""SCPI command item."""

		def __init__(self, name):
			"""Command have imperative form."""
			self.event = False
			"""Default child command."""
			self._default = None
			self.name = name
			"""Parent for composed instrument command."""
			self._parent = None
			"""Command have query form."""
			self.query = False
			"""Subcommands for composed commands."""
			self.subcmds = {}

		def addSubCommand(self, name):
			"""Return subcommand, if does not exists create new."""
			try:
				return self.getSubCommand(name)
			except KeyError:
				scpi_cmd = SCPISpecification.SCPI_cmd(name)
				scpi_cmd.setParent(self)
				self.subcmds[name] = scpi_cmd
				return scpi_cmd

		def getParent(self):
			return self._parent

		def getSubCommand(self, name):
			return self.subcmds[name]

		def getSubCommands(self):
			"""Return all subcommands sorted by name."""
			v = [x for x in self.subcmds.values()]
			v.sort(key = lambda x: x.name)
			return v

		def isCC(self):
			return self.name[0] == '*'

		def isIC(self):
			return self.name[0] != '*'

		def isOptional(self):
			if not self._parent:
				return False
			return self._parent._default == self

		def setEvent(self, event):
			self.event = event

		def setOptional(self):
			self._parent._default = self

		def setParent(self, scpi_cmd):
			self._parent = scpi_cmd

		def setQuery(self, query):
			self.query = query

	def __init__(self):
		self._scpi_cmds = self.SCPI_cmd(None)

	def fromFile(self, file_name):
		f = open(file_name, 'r')
		self.fromString(f.read())

	def fromString(self, scpi_spec):
		self._parseSpecification(scpi_spec)

	def _parseCC(self, cmd):
		query = False
		if cmd.endswith('?'):
			cmd = cmd[:-1]
			query = True
		cmd = cmd.upper()
		cmd = self._scpi_cmds.addSubCommand(cmd)
		if query:
			cmd.setQuery(True)
		else:
			cmd.setEvent(True)

	def _parseIC(self, cmd):
		"""Parse instrument command definition"""

		"""Get parrent command."""
		lvl = 0
		while cmd[lvl] == '\t':
			lvl = lvl + 1
		cmd = cmd[lvl:]
		while lvl < self._last_ic_lvl:
			self._last_ic_lvl = self._last_ic_lvl - 1
			self._last_ic_cmd = self._last_ic_cmd.getParent()
		if lvl > self._last_ic_lvl:
			raise ValueError('Invalid tab indendation, level of command (%i) is greater than level of parent (%i).'
					% (lvl, self._last_ic_lvl))

		"""Separate CMD from rest of line: CMD | params"""
		cmd = cmd.replace('\t', ' ').split(' ', 1)
		params = "" if len(cmd) == 1 else cmd[1].strip()
		cmd = cmd[0].strip()

		while cmd:
			optional = (cmd[0] == '[')
			cmd_name = None
			if optional:
				cmd_name, cmd = cmd[1:].split(']', 1)
			else:
				x = 1
				while x < len(cmd):
					if not (cmd[x].isalnum() or cmd[x] == '_'):
						break
					x = x + 1
				cmd_name, cmd = cmd[:x], cmd[x:]
			if cmd_name[0] == ':':
				cmd_name = cmd_name[1:]
			cmd_name = cmd_name.upper()

			self._last_ic_lvl = self._last_ic_lvl + 1
			self._last_ic_cmd = self._last_ic_cmd.addSubCommand(cmd_name)
			if optional:
				self._last_ic_cmd.setOptional()
			"""This is just lower level of command in command tree"""
			if cmd == '?':
				self._last_ic_cmd.setQuery(True)
				break
			if not cmd:
				self._last_ic_cmd.setEvent(True)

	def _parseSpecification(self, scpi_spec):
		self._last_ic_cmd = self._scpi_cmds
		self._last_ic_lvl = 0
		for l in scpi_spec.splitlines():
			l = l.rstrip()
			if not l or l.startswith('#'):
				continue
			if l.startswith('*'):
				self._parseCC(l)
				continue
			self._parseIC(l)

	def scpi_cmds(self):
		return self._scpi_cmds


class SCPI2cpp:
	def __init__(self, scpi_spec):
		self.scpi_spec = scpi_spec

	def _genCmdDecl(self, scpi_cmd):
		cmd = ""
		cmd_end = ""
		parent = scpi_cmd.getParent()
		while parent is not None:
			if not parent.name is None:
				cmd = 'namespace ' + parent.name + '{\n' + cmd
				cmd_end = cmd_end + '}\n'
			parent = parent.getParent()
		if scpi_cmd.isOptional():
			pass
		else:
			if scpi_cmd.query:
				cmd = cmd + scpi_cmd.name + "q(CmdBuilder *cmdBuilder);\n"
			if scpi_cmd.event:
				cmd = cmd + scpi_cmd.name + "e(CmdBuilder *cmdBuilder);\n"
		return cmd + cmd_end

	def _dumpCmds(self, scpi_cmds=None, lvl=0):
		cmds = []
		if scpi_cmds is None:
			scpi_cmds = self.scpi_spec.scpi_cmds()

		for sub_cmd in scpi_cmds.getSubCommands():
			sep = '' if lvl == 0 else ':'
			cmd = None
			if sub_cmd.isOptional():
				cmd = '\t' * lvl + '[' + sep + sub_cmd.name + ']'
			else:
				cmd = '\t' * lvl + sep + sub_cmd.name
			if sub_cmd.event:
				cmds.append(cmd)
			if sub_cmd.query:
				cmds.append(cmd + '?')
			if not sub_cmd.event and not sub_cmd.query:
				cmds.append(cmd)
			sub_dump = self._dumpCmds(sub_cmd, lvl + 1)
			if sub_dump:
				cmds.append(sub_dump)
		return '\n'.join(cmds)

	def generate(self, class_name, dest_dir):
		"""Parse SCPI specifiaction added by addSpecification(...) and write C++
classes into dest_dir."""
		file_name = class_name.lower()
		decl_file_name = file_name + '.hh'
		def_file_name = file_name + '.cpp'
		fdecl = open(os.path.join(dest_dir, decl_file_name), 'w')
		fdef = open(os.path.join(dest_dir, def_file_name), 'w')

		print(self._dumpCmds())
		#cmds = [self._genCmdDecl(scpi_cmd) for scpi_cmd in self.scpi_spec.scpi_cc()]

		#for key in self.scpi_spec.scpi_ic().getSubCommands():
		#	print(key.name)

		#cmds = "\n".join(cmds)
		return
		fdecl.write(Template("""#pragme once

#include "scpi_ifce.hh"

namespace ${main_ns} {

${cmds}
}
""").substitute(main_ns=class_name, cmds=cmds))


if __name__ == '__main__':
	cpp_dir = "./gen"
	class_name = "TestDevice"

	cc_file_name = "scpi_cc.txt"
	ic_file_name = "scpi_ic.txt"

	specifiaction = SCPISpecification()
	specifiaction.fromFile(cc_file_name)
	specifiaction.fromFile(ic_file_name)

	scpi2cpp = SCPI2cpp(specifiaction)
	scpi2cpp.generate(class_name, cpp_dir)

