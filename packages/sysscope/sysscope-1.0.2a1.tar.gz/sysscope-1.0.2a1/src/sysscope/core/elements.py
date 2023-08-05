

# TODO

class TemplateName:
	def __init__(self):
		self.rrdgraph_opts = []
	def add(self, opt):
		self.rrdgraph_opts.append(opt)
	def rrdgraph_options(self):
		return self.rrdgraph_opts
	def process(self, data):
		"""Override."""
		pass




