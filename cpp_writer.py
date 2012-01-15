
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

