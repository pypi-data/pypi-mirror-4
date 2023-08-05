def printlol(name):
    for eachitem in name:
	    if(isinstance(eachitem,list)):
		    printlol(eachitem)
	    else:
		    print(eachitem)
