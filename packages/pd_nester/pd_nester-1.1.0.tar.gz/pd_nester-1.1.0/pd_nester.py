def printlol(name,level):
    for eachitem in name:
	    if(isinstance(eachitem,list)):
		    printlol(eachitem,level+1)
	    else:
		    for each_tab in range(level):
			    print(eachitem)
		    print(eachitem)
