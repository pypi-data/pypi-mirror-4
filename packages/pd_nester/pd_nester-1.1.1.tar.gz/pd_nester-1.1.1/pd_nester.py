def printlol(name,level=0):
    for eachitem in name:
	    if(isinstance(eachitem,list)):
		    printlol(eachitem,level+1)
	    else:
		    for each_tab in range(level):
			    print("\t",end="")
		    print(eachitem)
