class iteratorList:
	def __init__(self):
		print("构造器")
	def iterator(array,level):
                print("*******************************")
		for a in array:
			if isinstance(a,list):
				ite.iterator(a,level)
			else:
				print(a)
                print("*******************************")
