#!/usr/bin/env python
import os

def vm_root_grabber():
	"""Returns the path to the vm root so you can add it to your sys.path
	"""
	splitcharacter='/'
	my_path = os.path.realpath(__file__)
	path_list = my_path.split(splitcharacter)
	path_list.pop(0)
	if 'src' in path_list:
		vm_root_list = []
		for dir in path_list[:path_list.index('src')]:
			string_to_add = splitcharacter +dir
			vm_root_list.append(string_to_add)
	elif 'site-packages' in path_list:
		vm_root_list = []
		for dir in path_list[:path_list.index('lib')]:
			string_to_add = splitcharacter +dir
			vm_root_list.append(string_to_add)
	vm_root = ''.join(vm_root_list)
	return vm_root
