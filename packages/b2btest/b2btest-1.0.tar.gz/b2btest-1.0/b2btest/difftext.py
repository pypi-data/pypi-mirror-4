#! /usr/bin/python
import os

def differences(expected, result, diffbase) :
	extension = os.path.splitext(result)[-1]
	difftxt = diffbase+extension
	are_equal = os.system("diff %s %s > %s" % (expected, result, difftxt) ) == 0
	if are_equal: return []
	return [
		"The result file \033[31m%s\033[0m is different to the expected \033[31m%s\033[0m"%(result,expected),
		]

