

def nestedPrintList(anyList, indent = False, nestedLevel=0):

    for eachItem in anyList:

        if isinstance(eachItem, list):
            nestedPrintList(eachItem, indent, nestedLevel+1)

        else:

            if indent:
                
                for tabSpace in range(nestedLevel):
                    print("\t", end='')
                
            print(eachItem)
            
