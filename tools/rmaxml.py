import os, re, sys
l = []
for r,d,f in os.walk(sys.argv[1]):
    f = map(lambda x: (lambda y: os.path.join(y,x))(r), filter(re.compile("\.axml$", re.I).search, f))
    if f: l.extend(f)
print "removing: ", l
map(os.unlink, l)
