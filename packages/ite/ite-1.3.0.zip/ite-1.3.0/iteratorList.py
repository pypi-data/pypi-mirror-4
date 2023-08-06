class iteratorList:
	def __init__(array):
		self.array = array
	def iterator(level):
		for a in self.array:
			if isinstance(a,list):
				self.iterator(a,level)
			else:
				print(a)

