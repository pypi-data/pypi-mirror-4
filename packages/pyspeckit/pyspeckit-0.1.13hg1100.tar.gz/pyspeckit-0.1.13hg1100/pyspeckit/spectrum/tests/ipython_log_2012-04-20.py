########################################################
# Started Logging At: 2012-04-20 11:21:03
########################################################

get_ipython().magic(u'run test_units.py')
get_ipython().system(u'cat test_units.py')
test_convert_back('MHz','km/s')
test_convert_back('MHz','km/s','optical')
get_ipython().magic(u'pdb')
test_convert_back('MHz','km/s','optical')
########################################################
# Started Logging At: 2012-04-20 11:27:48
########################################################

get_ipython().magic(u'run test_units.py')
get_ipython().magic(u'pdb')
test_convert_back('hz','km/s','radio')
########################################################
# Started Logging At: 2012-04-20 11:29:06
########################################################

get_ipython().magic(u'run test_units.py')
test_convert_back('cm/s','a','radio')
test_convert_back('centimeters/s','a','radio')
get_ipython().magic(u'pdb')
test_convert_back('centimeters/s','a','radio')
