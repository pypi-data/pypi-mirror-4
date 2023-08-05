#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


"""
Take cotrol of top header of every file,
apply the tmpl supplied

SHould handle all file types not just python

Hdr block is, starting at first line in file,
any and all contiguous lines that begin with a #
or are blank.

Once we reach a line not meeting that criteria, the hdr block has ended.

useage:

    ### find /my/code -type f \( -iname "*.py" -o -iname "*.js" \) -exec fileheadermaker.py '{}' \;
    ### git add -i
        (add the ones you meant to change)
    ### git commit ...
    ### git reset --hard 
        (remoes the changes forced on some thiord party .js file in your tree...)


"""
import shutil
import sys
import os

def lineishdr(l):
    """ 
    Determine is a line *at top of a file* is a header, or if its body

    We simply assume that the header of a file is a contiguous block of 
    comment and blank lines.  Anything else triggers "no longer header" flag


    >>> lineishdr("#!/usr/local/bin/python")
    True
    >>> lineishdr("  ")
    True
    >>> lineishdr(" #!/usr/local/bin/python")
    False
    >>> lineishdr("import os")
    False

    >>> lineishdr("// THis is JS")
    True
    >>> lineishdr("function foo()")
    False

    """
    if l.find("#") == 0:
        return True
    elif l.find("//") == 0:
        return True
    elif l.strip() == '':
        return True
    else:
        return False

pytmpl = """#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


"""

jstmpl = """// Copyright (c) Rice University 2012
// This software is subject to 
// the provisions of the GNU Lesser General
// Public License Version 2.1 (LGPL).
// See LICENCE.txt for details.  
//


"""

tmpls = {'.py': pytmpl,
         '.js': jstmpl
        }



def do(f, tmpf):
    """
    
    """
    
    ext = os.path.splitext(f)[1]
    tmpl = tmpls[ext]
    

    tmpfo = open(tmpf, 'w')
    orig_hdr = ''
    body = '' 
    hdrflag = 0
    for line in open(f):

        if (lineishdr(line) and hdrflag == 0):
            orig_hdr += line
        else:
            hdrflag = 1
            body += line
    tmpfo.write(tmpl)
    tmpfo.write(body)
    tmpfo.close()

    shutil.move(tmpf, f)


if __name__ == '__main__':



    f = sys.argv[1:][0]

    #finangle not having lib vs exe script.
    if f == 'doctest':
        import doctest
        doctest.testmod()
        sys.exit()
   

    if not os.path.isfile(f): 
        raise OSError("%s must be a file" % f)
    validexts = [".py", ".js"]
    if os.path.splitext(f)[1] not in validexts:
        raise OSError("%s must be a file with %s ext" % (f, ','.join(validexts)))

    print "adjusting %s" % f,
    #awful use tmpfile
    do(f, '/tmp/foo.txt')
    print " done"

    
