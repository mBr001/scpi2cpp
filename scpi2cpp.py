#!python3

import os.path
from string import Template


class SCPISpecification:
	class SCPI_cmd:
		"""SCPI command item."""

		def __init__(self, name):
			"""Command have imperative form."""
			self.event = False
			self.name = name
			"""Command is optional/default."""
			self.optional = False
			"""Parent for composed instrument command."""
			self._parent = None
			"""Command have query form."""
			self.query = False
			"""Subcommands for composed commands."""
			self.subcmds = {}

		def addSubCommand(self, name):
			"""Return all subcommands sorted by name."""
			scpi_cmd = SCPISpecification.SCPI_cmd(name)
			self.subcmds[name] = scpi_cmd
			scpi_cmd.setParent(self)
			return scpi_cmd

		def getParent(self):
			return self._parent

		def getSubCommand(self, name):
			return self.subcmds[name]

		def getSubCommands(self):
			v = [x for x in self.subcmds.values()]
			v.sort(key = lambda x: x.name)
			return v

		def isCC(self):
			return self.name[0] == '*'

		def isIC(self):
			return self.name[0] != '*'

		def setEvent(self, event):
			self.event = event

		def setOptional(self, optional):
			self.optional = optional

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

	def _parseIC(self, cmd):
		query = False
		if cmd.endswith('?'):
			cmd = cmd[:-1]
			query = True
		cmd = cmd.upper()
		try:
			cmd = self._scpi_cmds.getSubCommand(cmd)
		except KeyError:
			cmd = self._scpi_cmds.addSubCommand(cmd)

		if query:
			cmd.setQuery(True)
		else:
			cmd.setEvent(True)

	def _parseSpecification(self, scpi_spec):
		last_ic_cmd = []
		for l in scpi_spec.splitlines():
			l = l.rstrip()
			if not l or l.startswith('#'):
				continue
			if l.startswith('*'):
				self._parseIC(l)
				continue

			"""Parse instrument command definition"""

			"""Get parrent command."""
			lvl = 0
			scpi_ic = self._scpi_ic
			while l[lvl] == '\t':
				scpi_ic = scpi_ic.subcmds[last_ic_cmd[lvl]]
				lvl = lvl + 1
			l = l[lvl:]
			last_ic_cmd = last_ic_cmd[:lvl]

			"""Split line to: CMD params [options]"""
			l = l.replace('\t', ' ').split(' ', 1)
			cmd = l[0].strip()
			params = "" if len(l) == 1 else l[1]
			params = params.strip().split('[', 1)
			options = "" if len(params) == 1 else params[1].strip()
			params = params[0].strip()

			while True:
				optional = (cmd[0] == '[')
				c = None
				if optional:
					c, cmd = cmd.split(']', 1)
				else:
					a = cmd.find(':', 1)
					b = cmd.find('[', 1)
					x = len(cmd)
					if a >= 0:
						x = a
					if b >= 0 and b < x:
						x = b
					c, cmd = cmd[:x], cmd[x:]
				if c[0] == ':':
					c = c[1:]
				query = True
				event = True
				if c[-1] == '?':
					event = False
				
				c = c.upper()
				last_ic_cmd.append(c)
				new_scpi_ic = scpi_ic.addSubCommand(c)
				new_scpi_ic.setEvent(event)
				new_scpi_ic.setOptional(optional)
				new_scpi_ic.setQuery(query)
				if not cmd:
					break

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
		if scpi_cmd.optional:
			pass
		else:
			if scpi_cmd.query:
				cmd = cmd + scpi_cmd.name + "q(CmdBuilder *cmdBuilder);\n"
			if scpi_cmd.event:
				cmd = cmd + scpi_cmd.name + "e(CmdBuilder *cmdBuilder);\n"
		return cmd + cmd_end

	def _dumpCmds(self, lvl=0):
		cmds = []
		cc = self.scpi_spec.scpi_cmds()
		for sub_cmd in cc.getSubCommands():
			sep = '' if lvl == 0 else ':'
			cmd = '\t' * lvl + sep + sub_cmd.name
			if (sub_cmd.event):
				cmds.append(cmd)
			if (sub_cmd.query):
				cmds.append(cmd + '?')
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

