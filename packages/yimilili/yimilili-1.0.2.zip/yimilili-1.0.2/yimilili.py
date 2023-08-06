#python 3
'''
   yimilili's first py module
   include  print_listoflist(list, isSuojin=True, level=0)
'''
print("hello world")
print("nihao")
def print_listoflist(list, isSuojin=True, level=0):
	for each_item in list:
		if isinstance(each_item, list):
			print_listoflist(each_item, isSuojin, level+1)

		else:
			if isSuojin:
				print('\t'*level,"end=''")
			print(each_item)
