"""迭代列表
"""
def ite(arrays,indent=False,level=0):
	
	for a in arrays:
		if isinstance(a,list):
			ite(a,indent,level+1)
		else:
                        if indent:
                                for i in range(level):
                                        print("\t",end='')
                        print(a)
	
