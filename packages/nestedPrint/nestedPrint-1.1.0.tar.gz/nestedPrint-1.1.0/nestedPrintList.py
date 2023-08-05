

def nestedPrintList(anyList, nestedLevel):

    for eachItem in anyList:

        if isinstance(eachItem, list):
            nestedPrintList(eachItem, nestedLevel+1)

        else:
            for tabSpace in range(nestedLevel):
                print("\t", end='')
                
            print(eachItem)
            
