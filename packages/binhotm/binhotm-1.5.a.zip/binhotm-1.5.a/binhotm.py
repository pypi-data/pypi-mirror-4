"""Modulo da funcao print lista"""
"""By: Fabricio Junior da Silva"""

def print_list(the_list, level=0):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_list(each_item, level+1)
		else:
                        for num in range(level):
                                print("\t", end='')
                        print(each_item)
			
