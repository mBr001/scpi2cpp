#!python3

import os.path
from string import Template


class ClassWriter:
	"""Write C++ class definition and declaration into files."""

	prot_private = 'private:\n'
	prot_protected = 'protected:\n'
	prot_public = 'public:\n'
	protection = prot_public

	class Item:
		"""C++ class item, eg. function, variable, constant."""

		class Declaration:
			def __init__(self, ret_type, name):
				self.ret_type = ret_type
				self.name = name

			def get(self, namespace = ""):
				if namespace:
					namespace = namespace + "::"
				if self.ret_type:
					return self.ret_type + " " + namespace + self.name
				return namespace + self.name

		def __init__(self, protection, declaration, definition):
			self._declaration = declaration
			self._definition = definition
			self.protection = protection

		def declaration(self, namespace = ""):
			return self._declaration.get(namespace)

		def definition(self):
			return self._definition

	def __init__(self, name, parent = None):
		self.name = name
		self.parent = parent
		self.indent = 0 if parent is None else parent.indent + 1
		self.items = []

	def addItem(self, protection, declaration, definition):
		self.items.append(self.Item(protection, declaration, definition))

	def addFunc(self, name, body):
		pass

	def addTypedef(self, name, class_writer):
		pass

	def addSubclass(self, name):
		c = ClassWriter(name, self)
		self.items.append(c)
		return c

	def declaration(self):
		items = ""
		protection = self.prot_private
		for i in self.items:
			if i.protection != protection:
				protection = i.protection
				items = items + protection
			items = items + "\t" + i.declaration() + ';\n'

		t = Template("""class ${class_name} {
${items}
};
""")
		return t.substitute(class_name=self.name, items=items)

	def definition(self, header_file_name=None):
		items = ""
		if not header_file_name is None:
			items = Template("""#include "${header_file_name}"\n\n""")
			items = items.substitute(header_file_name=header_file_name)
		t = Template("${declaration}${definition}\n")
		for i in self.items:
			if isinstance(i ,ClassWriter):
				items = items + i.definition()
			else:
				items = items + t.substitute(class_name=self.name,
						declaration=i.declaration(self.namespace()),
						definition=i.definition())
		return items

	def namespace(self):
		if self.parent:
			return self.parent.namespace() + "::" + self.name
		return self.name


class SCPI2cpp:
	class SCPI_IC:
		"""SCPI instrument command item."""
		def __init__(self):
			self.subcmds = {}
			"""Command is optional/default"""
			self.optional = False
			"""Command have query form."""
			self.query = True
			"""Command have imperative form."""
			self.event = True

		def addSubCommand(self, name, scpi_ic):
			self.subcmds[name] = scpi_ic
			scpi_ic.setParent(self)

		def setEvent(self, event):
			self.event = event

		def setOptional(self, optional):
			self.optional = optional

		def setParent(self, parent_ic):
			self.parent_ic = parent_ic

		def setQuery(self, query):
			self.query = query

	def __init__(self):
		self.scpi_spec = ""

	def addSpecification(self, scpi_spec):
		self.scpi_spec = "%s\n%s" % (self.scpi_spec, scpi_spec)

	def generate(self, class_name, dest_dir):
		"""Parse SCPI specifiaction added by addSpecification(...) and write C++
classes into dest_dir."""
		file_name = class_name.lower()
		dec_file_name = file_name + '.hh'
		def_file_name = file_name + '.cpp'
		fdec = open(os.path.join(dest_dir, dec_file_name), 'w')
		fdef = open(os.path.join(dest_dir, def_file_name), 'w')

		self.parseSpecification()

		c = ClassWriter(class_name)
		c.addItem(c.prot_public, c.Item.Declaration("", class_name+"()"), """
{
}
""")
		for name, scpi_cmd in self.scpi_cc.items():
			subclass = c.addSubclass(name)
			subclass.addItem(c.prot_public, c.Item.Declaration("", name+"()"), """
{
}
""")

		for ic in self.scpi_ic.subcmds.items():
			print(ic)

		fdec.write(c.declaration())
		fdef.write(c.definition(dec_file_name))

	def parseSpecification(self):
		self.scpi_cc = {}
		self.scpi_ic = self.SCPI_IC()
		last_ic_cmd = []
		for l in self.scpi_spec.splitlines():
			l = l.strip()
			if l.startswith('#') or not l:
				continue
			if l.startswith('*'):
				l = l[1:].strip()
				query = False
				if l.endswith('?'):
					l = l[:-1]
					query = True
				try:
					cmd = self.scpi_cc[l]
					if query:
						cmd.setEvent(True)
					else:
						cmd.setEvent(True)
				except KeyError:
					cmd = self.SCPI_IC()
					if query:
						cmd.setEvent(False)
					else:
						cmd.setQuery(False)
					self.scpi_cc[l] = cmd
				continue

			"""Parse instrument command definition"""

			"""Get command level"""
			lvl = 0
			scpi_ic = self.scpi_ic
			while l[lvl] == '\t':
				scpi_ic = scpi_ic.subcmds[last_ic_cmd[lvl]]
				lvl = lvl + 1
			l = l[lvl:]
			last_ic_cmd = last_ic_cmd[:lvl]

			"""Split line to: CMD params [options]"""
			l = l.replace('\t', ' ').split(' ', 1)
			cmd = l[0].strip().split(':')
			params = "" if len(l) == 1 else l[1]
			params = params.strip().split('[', 1)
			options = "" if len(params) == 1 else params[1].strip()
			params = params[0].strip()

			if not cmd[0]:
				cmd = cmd[1:]
			optional = False
			if cmd[0] == '[':
				optional = True
				cmd = cmd[1:]
			elif cmd[0].startswith('['):
				optional = True
				cmd[0] = cmd[0][1:]
			if optional:
				cmd[0] = cmd[0][:-1]
			last_ic_cmd.append(cmd[0])
			new_scpi_ic = self.SCPI_IC()
			new_scpi_ic.setOptional(optional)
			scpi_ic.addSubCommand(cmd[0], new_scpi_ic)


		print(repr(self.scpi_cc))
		print(repr(self.scpi_ic))


if __name__ == '__main__':
	cpp_dir = "./gen"
	class_name = "TestDevice"

	cc_file_name = "scpi_cc.txt"
	ic_file_name = "scpi_ic.txt"

	scpi2cpp = SCPI2cpp()

	specifiaction = open(cc_file_name).read()
	scpi2cpp.addSpecification(specifiaction)

	specifiaction = open(ic_file_name).read()
	scpi2cpp.addSpecification(specifiaction)

	scpi2cpp.generate(class_name, cpp_dir)

