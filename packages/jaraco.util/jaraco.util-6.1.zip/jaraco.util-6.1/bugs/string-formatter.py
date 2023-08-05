import random
class MyDynamicObject:
	def __getitem__(self, name):
		return name + ' ' + str(random.randint(1,10))

print("%(foo)s" % MyDynamicObject()) # works!
if hasattr('', 'format_map'):
	print("{foo}".format_map(MyDynamicObject())) # works on Python 3.2+
else:
	print("{foo}".format(**MyDynamicObject()))
	# can't do that because MyDynamicObject can't enumerate every possible
	#  kwparam
	# fails with TypeError: format() argument after ** must be a mapping,
	#  not instance.

