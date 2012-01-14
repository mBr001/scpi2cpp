#!python3


class SCPI2cpp:
	def __init__(self):
		self.scpi_spec = ""

	def addSpecification(self, scpi_spec):
		self.scpi_spec = "%s\n%s" % (self.scpi_spec, scpi_spec)

	def generate(self, dest_dir):
		"""Parse SCPI specifiaction added by addSpecification(...) and write C++
classes into dest_dir."""
		pass


if __name__ == '__main__':
	cpp_dir = "./gen"
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
	scpi2cpp.generate(cpp_dir)
	
