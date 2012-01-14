#!python3

import os.path
from string import Template


class ClassWriter:
	def __init__(self, name, parent = None):
		self.name = name
		self.parent = parent
		if parent is None:
			self.indent = 0
		else:
			self.indent = parent.indent + 1
		self.indent0 = "\t" * self.indent
		self.indent1 = "\t" * (self.indent + 1)

	def addFunc(self, name, body):
		pass

	def addTypedef(self, name, class_writer):
		pass

	def addSubclass(self, name):
		return ClassWriter(name, self)

	def declaration(self):
		t = Template("""class ${class_name} {
public:
	${class_name}();
};
""")
		return t.substitute(class_name=self.name)

	def definition(self, header_file_name):
		t = Template("""#include "${header_file_name}"
${class_name}::${class_name}()
{
}
""")
		return t.substitute(header_file_name=header_file_name,
				class_name=self.name)


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
	
