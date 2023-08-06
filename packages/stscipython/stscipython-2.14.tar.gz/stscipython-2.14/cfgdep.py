import sys
import glob
import ConfigParser
import re
import os

# the setup.cfg is a config parser object; it is easier to use as
# a nested dictionary.
def config_parser_to_dict(c) :
    d = { }
    for sect in c.sections() :
        d[sect] = { }
        for name, value in c.items(sect) :
            d[sect][name]=value
    return d

# split the requires list into a list of just package names
def split_requires(s) :
    il = s.split('\n')
    ol = [ ]
    for x in il :
        x = x.strip()
        a = x.split('#')[0]
        b = x.split(';')[0]
        if len(a) < len(b) :
            x = a
        else :
            x = b
        x = parens.sub(' ', x)
        x = x.strip()
        if x == '' :
            continue
        ol.append(x)
    return ol


# all_nodes is all of the packages that we require
all_nodes = { }

class package_node(object):
    pass

parens = re.compile('\([^)]*\)')

####

# -c means read the list of packages from the setup.cfg for stsci-python
if '-c' in sys.argv :
    c = ConfigParser.RawConfigParser()
    c.read("setup.cfg")
    d = config_parser_to_dict(c)
    if not 'requires-dist' in d['metadata'] :
        print "no requires-dist in metadata!"
        sys.exit(1)

    if len(d) == 0 :
        print "no packages listed in cfg file"
        sys.exit(1)

    pkglist = split_requires(d['metadata']['requires-dist'] )

# -i means read the list of packages from stdin; use stp_list | python cfgdep.py -i ...
elif '-i' in sys.argv :
    pkglist = [ ]
    for x in sys.stdin :
        x = x.split()
        if x[0].strip() == 'new_install' :
            continue
        pkglist.append(x[0])

else :
    print "use -c to read setup.cfg"
    print "use -i to read stdin"
    print "   for list of packages"
    print "e.g. stp_list | python cfgdep.py -i"
    sys.exit(1)

####

new = { }       # has an entry for each thing that is already using the new setup

versions = { }  # has an entry for the version number of each package

####

# for every package that is in stsci-python
for x in pkglist :

    # read that packages setup.cfg
    f = None

    try :
        f = open( x + "/setup.cfg" )
        new[x] = 1
    except IOError :
        try :
            f = open( x + "/new_setup.cfg" )
        except IOError :
            print "NO CFG FOR ",x
            # os.system("ls -l %s"%x)
            sys.exit(1)
            continue

    c = ConfigParser.RawConfigParser()
    c.readfp(f)

    # make the dependency list into a dict
    d = config_parser_to_dict(c)

    # make an entry for the current package
    node = package_node()
    node.name = d['metadata']['name']
    if 'requires-dist' in d['metadata'] :
        node.requires = split_requires( d['metadata']['requires-dist'] )
    else :
        node.requires = [ ]
        node.depth = 0

    # remember the version of the current package
    versions[node.name] = d['metadata']['version']

    all_nodes[node.name] = node

# dict with an entry for each missing required package
# initialize it with the packages we don't care about, to suppress
# those error messages
missing = { 
    'setuptools' : 1,
    'numpy' : 1,
    }

# recursively find all the required packages, even those required
# by other packages that we require.  all_nodes[n].requires is the list.
def find_requires(n, depth) :
    # print '  ' * depth, 'want', n
    depth = depth + 1
    if not n in all_nodes :
        if not n in missing :
            print "MISSING ",n
            missing[n] = 1
        return [ n ]

    if all_nodes[n].depth < depth :
        all_nodes[n].depth = depth
        
    l = all_nodes[n].requires
    for x in all_nodes[n].requires :
        l = l + find_requires(x, depth)

    l = list(set(l))
    all_nodes[n].requires = l
    # print '  ' * depth, l
    return l

#

for x in all_nodes :
    all_nodes[x].depth = 0

for x in all_nodes :
    find_requires(x,0)

l = [ ( all_nodes[x].depth, x ) for x in all_nodes ]
l = sorted(l)
l.reverse()


if '-status' in sys.argv :
    l = [ ( all_nodes[x].depth, x, new.get(x,0), versions[x] ) for x in all_nodes ]
    l = sorted(l)
    l.reverse()
    import pandokia.text_table as text_table
    t = text_table.sequence_to_table(l)
    print t.get_rst()

# list the packages in the order that you should install them
if '-order' in sys.argv :
    l = [ ( all_nodes[x].depth, x, new.get(x,0), versions[x] ) for x in all_nodes ]
    l = sorted(l)
    l.reverse()
    for x in l :
        print x[1]

# list the packages in the order that you should install them, and
# list all the prerequisites in the order you should install them
# too.
if '-nest' in sys.argv :
    for x in all_nodes :
        print x, all_nodes[x].requires

# list it as a dict of package and version
if '-dict' in sys.argv:
    print "{"
    for x in all_nodes :
        print "'%s' : '%s',"%(x,versions[x])
    print "}"

# write the discovered information into a new setup.cfg file
if '-cfgupdate' in sys.argv :
    fi = open("setup.cfg","r")
    fo = open("new_setup.cfg","w")
    while 1 :
        x = fi.readline()
        if x == '' :
            break
        if x.startswith('requires-dist =') :
            fo.write('requires-dist = \n')
            for p in l :
                name = p[1]
                fo.write('\t%s (%s)\n'%(name,versions[name]))
                if 'dev' in versions[name] :
                    print "DEV VERSION",name,versions[name]
            while 1 :
                x = fi.readline()
                if x == '' :
                    raise ValueError('never saw # end requires-dist')
                if x.startswith('# end requires-dist') :
                    fo.write(x)
                    break
        else :
            fo.write(x)


