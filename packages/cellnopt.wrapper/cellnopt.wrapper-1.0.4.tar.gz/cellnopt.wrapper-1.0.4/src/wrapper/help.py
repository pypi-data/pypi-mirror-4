# -*- python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: http://www.ebi.ac.uk/saezrodriguez/cno
#
##############################################################################


helppages = {}

try:
    import wrapper_cnor
    helppages["wrapper_cnor"]=  wrapper_cnor.__all__
except:
    pass

try:
    import wrapper_ode
    helppages["wrapper_ode"]=  wrapper_ode.__all__
except:
    pass

try:
    import wrapper_fuzzy
    helppages["wrapper_fuzzy"]=  wrapper_fuzzy.__all__
except:
    pass

try:
    import tools
    helppages["tools"] = tools.__all__
except:
    pass

def cnohelp(func=None):
    """Opens a tab in a browser showing the on-line help of a function.

    ::

        >>> cnohelp("readMIDAS")
    
    """
    if func == None:
        msg = "Available help page are \n"
        for k in sorted(helppages.keys()):
            msg += k.upper() +"\n\n"
            funcs = sorted(helppages[k])
            for func in funcs:
                msg += " - "+func+"\n"
        print msg
        return

    #otherwise
    for module in helppages.keys():
        if func in helppages[module]:
            url = "http://www.ebi.ac.uk/~cokelaer/cellnopt/wrapper/references.html#cellnopt.wrapper.%s.%s" %(module,func)
            try:
                import webbrowser
                print url
                webbrowser.open_new_tab(url)
                return
            except:
                print("Could not parser url...")
    # if we are here, func was not found
    raise ValueError("%s name could not be found. typ cnohelp() without argument to get the list of available names" %func)
