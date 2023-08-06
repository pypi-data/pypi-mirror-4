import ziptax

ziptax.ZIPTAX_API_KEY = 'asdfasdf'

# Getting tax rate for zipcode
print ziptax.get_tax_rate(32725)
# 0.064999997615814

# Catch Errors
try:
    tax_rate = ziptax.get_tax_rate(23452)
except ziptax.Ziptax_Failure, e:
    print "FAILUED DUE TO %s" % e