"""Modulo da funcao print lista"""
"""By: Fabricio Junior da Silva"""

def print_list(the_list, tamanho):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_list(each_item, tamanho+1)
		else:
                        for num in range(tamanho):
                                print("\t", end='')
			print(each_item)


