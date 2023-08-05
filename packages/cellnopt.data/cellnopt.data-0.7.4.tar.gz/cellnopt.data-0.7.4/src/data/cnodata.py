import os
from easydev import get_shared_directories

__all__ = ["cnodata", "build_filepaths"]

def build_filepaths():
    "returns a dictionary containing SIF/CSV files found in the share directory"
    datadirs = get_shared_directories("cellnopt.data", "data")
    filepaths = {}
    for d in datadirs:
        name = os.path.split(d)[1]
        for filename in os.listdir(d):
            ext = os.path.splitext(filename)[1]
            if ext in [".csv", ".CSV", ".SIF", ".sif"]:
                # is there an aliases.py file to get aliases from ?
                try:
                    exec(open(d + os.sep + "aliases.py","r").read())
                    aliases[filename]
                except:
                    # if not, let us jsut fill the aliases with an empty list
                    aliases = {filename:[]}
                filepaths[filename] = {
                    'path':d+os.sep+filename,
                    'name':name,
                    'origin':'cellnopt.data',
                    'aliases': aliases[filename]}
    return filepaths

def cnodata(filename, local=False, verbose=False):
    c = CNOData(verbose=verbose)
    p = c.cnodata(filename, local=local)
    return p



class CNOData(object):
    """class to ease manipulation of the shared directories to retrieve data

    ::

        c = CNOData()
        c.package_data
        c.cnodata("ToyMMB.sif")

    """
    def __init__(self, verbose=True, web=False):

        self.package_data = build_filepaths()
        self.verbose = verbose
        self.check()

    def _get_aliases(self):
        aliases = []
        for k, v in self.package_data.iteritems():
            for a in self.package_data[k]['aliases']:
                aliases.append(a)
        return aliases
    aliases = property(_get_aliases)

    def _get_filenames(self):
        filenames = self.package_data.keys()
        return filenames
    filenames = property(_get_filenames)

    def check(self):
        #aliases must not be found in keys
        aliases = self.aliases
        if len(set(aliases)) == len(aliases):
            return
        else:
            raise Exception("aliases duplication found. This must not happen. check package_data attribute")

    def cnodata(self, filename, local=True):
        # if local is true, we first want to try that option
        if local == True:
            if os.path.exists(filename):
                return filename
            else:
                raise IOError("filename %s not found in local directory" % filename)

        if filename in self.filenames:
            return self.package_data[filename]['path']
        elif filename in self.aliases:
            if self.verbose:
                print("%s not found in cellnopt.data directories. Checking for aliases" % filename)
            for k, v in self.package_data.iteritems():
                if filename in self.package_data[k]['aliases']:
                    print("%s is an alias of %s. Please use the latter filename." % (filename, k))
                    return self.package_data[k]['path']
        # now, if loca was false, we cannot be here. 
        # in addition, if filename not found in the pacakge, we can still try to
        # get here from the local directory !
        if os.path.exists(filename):
            return filename

        # finally, nothing found, shall we raise a warning ? error?
        if self.verbose:
            print("%s not found in cellnopt.data" % filename)
        return

    def __str__(self):
        from easydev import underline
        txt = ""
        dirs = sorted(self.package_data.keys())
        for d in dirs:
            txt += underline(d) + "\n"
            txt += " origin:"+ self.package_data[d]['name'] + "\n"
            txt += " aliases:"+ ", ".join([x for x in self.package_data[d]['aliases']]) + "\n"
            txt += " path:"+ self.package_data[d]['path'] + "\n"
            txt += "\n"
        return txt



