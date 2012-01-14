#!python3

import os.path
from string import Template


class ClassWriter:
	"""Write C++ class definition and declaration into files."""

	prot_private = 'private:\n'
	prot_protected = 'protected:\n'
	prot_public = 'public:\n'

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
			self.declaration = declaration
			self.definition = definition
			self.protection = protection

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
		return ClassWriter(name, self)

	def declaration(self):
		items = ""
		protection = self.prot_private
		for i in self.items:
			if i.protection != protection:
				protection = i.protection
				items = items + protection
			items = items + "\t" + i.declaration.get() + ';\n'

		t = Template("""class ${class_name} {
${items}
};
""")
		return t.substitute(class_name=self.name, items=items)

	def definition(self, header_file_name):
		items = Template("""#include "${header_file_name}"\n\n""")
		items = items.substitute(header_file_name=header_file_name)
		t = Template("${declaration}${definition}\n")
		for i in self.items:
			items = items + t.substitute(class_name=self.name,
					declaration=i.declaration.get(self.namespace()),
					definition=i.definition)
		return items

	def namespace(self):
		if self.parent:
			return self.parent.namespace() + "::" + self.name
		return self.name


class SCPI2cpp:
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

		c = ClassWriter(class_name)
		c.addItem(c.prot_public, c.Item.Declaration("", class_name+"()"), """
{
}
""")
		fdec.write(c.declaration())
		fdef.write(c.definition(dec_file_name))


if __name__ == '__main__':
	cpp_dir = "./gen"
	class_name = "TestDevice"
	scpi_spec = """
# this is comment

*OPC
ROUTe
	:CLOSe	<channel_list>
		:STATe?
	:OPEN	<channel_list>
		:ALL	[event; no query]
"""
	
	scpi2cpp = SCPI2cpp()
	scpi2cpp.addSpecification(scpi_spec)
	scpi2cpp.generate(class_name, cpp_dir)
	
