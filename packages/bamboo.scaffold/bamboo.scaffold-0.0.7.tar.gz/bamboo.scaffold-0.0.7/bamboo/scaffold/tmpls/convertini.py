import ConfigParser
import collections

appname = "bamboo"
filepath = "bamboo.ini"

parser = ConfigParser.SafeConfigParser()
parser.optionxform = str     #case sensitive                                           
parser.read(filepath)
d = collections.OrderedDict(parser.items(appname))

for k in d:
    print "export %s=%s" % (k,d[k])
	

