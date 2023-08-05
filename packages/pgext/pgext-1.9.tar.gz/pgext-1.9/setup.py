import os
import sys
import distutils.core
import json
import glob

SETUP_CFG_FILE = "setup.json"


# Get version of application
def getVersion(fpath):
    if not os.path.exists(fpath):
        return None
    version = None
    fp = open(fpath, "rb")
    for line in fp:
        if line.find("__version__") != -1:
            d = line.replace(
                " ", "").replace("\t", "").replace("\n", "").replace("\r", "")
            d = d.split("__version__=")
            version = d[1]
            break
    fp.close()
    return version


# Try to find path
def searchPath(patterns, basepaths):
    for basepath in basepaths:
        for pattern in patterns:
            paths = glob.glob(os.path.join(basepath, pattern))
            for path in paths:
                if os.path.exists(path):
                    path = os.path.dirname(path)
                    return path
    return None


class ConfigSetup:
    def __init__(self, config_file):
        if sys.platform == 'win32':
            self.plat = "win32"
        elif sys.platform == 'darwin':
            self.plat = "darwin"
        else:
            self.plat = "unix"

        fp = open(config_file, "rb")
        config = self.deunicode(json.load(fp))
        fp.close()

        self.version_file = config.get("version_file", None)
        self.metadata = config["metadata"]
        self.files = config["files"]
        self.config = {}

    def deunicode(self, obj):
        if isinstance(obj, dict):
            result = {}
            for key in obj:
                result[str(key)] = self.deunicode(obj[key])
            return result
        elif isinstance(obj, list):
            result = []
            for item in obj:
                result.append(self.deunicode(item))
            return result
        else:
            return str(obj)

    def configure_unix(self):
        self.ext_include_dirs = {}

        incdirs = ["/usr/include/", "/usr/local/include"]
        for name in self.files["ext_include"]:
            patterns = self.files["ext_include"][name]
            path = searchPath(patterns, incdirs)
            if path:
                self.ext_include_dirs[name] = path
                print "%s: %s" % (name, path)
            else:
                print "Include path not found (%s)" % name

        self.ext_library_dirs = {}

        libdirs = ['/usr/lib', '/usr/lib64', '/usr/X11R6/lib',
                   '/usr/local/lib', '/usr/local/lib64', '/usr/local/X11R6/lib']
        for name in self.files["ext_libraries"]:
            patterns = self.files["ext_libraries"][name]
            path = searchPath(patterns, libdirs)
            if path:
                self.ext_library_dirs[name] = path
                print "%s: %s" % (name, path)
            else:
                print "Library path not found (%s)" % name

    def configure_darwin(self):
        self.ext_include_dirs = {}

        incdirs = ['/usr/local/include', '/opt/local/include']
        for name in self.files["ext_include"]:
            patterns = self.files["ext_include"][name]
            path = searchPath(patterns, incdirs)
            if path:
                self.ext_include_dirs[name] = path
                print "%s: %s" % (name, path)
            else:
                print "Include path not found (%s)" % name

        self.ext_library_dirs = {}

        libdirs = ['/usr/local/lib', '/opt/local/lib']
        for name in self.files["ext_libraries"]:
            patterns = self.files["ext_libraries"][name]
            path = searchPath(patterns, libdirs)
            if path:
                self.ext_library_dirs[name] = path
                print "%s: %s" % (name, path)
            else:
                print "Library path not found (%s)" % name

    def configure_win32(self):
        self.ext_include_dirs = {}

        incdirs = ['../*', '*include*']
        for name in self.files["ext_include"]:
            patterns = self.files["ext_include"][name]
            path = searchPath(patterns, incdirs)
            if path:
                self.ext_include_dirs[name] = path
                print "%s: %s" % (name, path)
            else:
                print "Include path not found (%s)" % name

        self.ext_library_dirs = {}
        libdirs = ['../*', '*lib*', '*VisualC*', '*Release*']
        for name in self.files["ext_libraries"]:
            patterns = self.files["ext_libraries"][name]
            path = searchPath(patterns, libdirs)
            if path:
                self.ext_library_dirs[name] = path
                print "%s: %s" % (name, path)
            else:
                print "Library path not found (%s)" % name

    def configure(self):

        if self.plat == "unix":
            self.configure_unix()
        if self.plat == "darwin":
            self.configure_darwin()
        if self.plat == "win32":
            self.configure_win32()

        if "ext_modules" in self.files:
            self.config["ext_modules"] = []
            for exm in self.files["ext_modules"]:
                name = exm[0]
                sources = exm[1]
                libraries = exm[3]

                incdirs = []
                for incd in exm[2]:
                    incdirs.append(self.ext_include_dirs[incd])

                libdirs = []
                for libd in exm[3]:
                    libdirs.append(self.ext_library_dirs[libd])

                ex = distutils.core.Extension(name, sources,
                                              libraries=libraries,
                                              include_dirs=incdirs,
                                              library_dirs=libdirs,
                                              )
                self.config["ext_modules"].append(ex)
                print "Extension: %s" % name

        for key in self.files:
            if key in ("ext_libraries", "ext_include", "ext_modules"):
                continue
            self.config[key] = self.files[key]

        for key in self.metadata:
            self.config[key] = self.metadata[key]

        if self.version_file:
            ver = getVersion(self.version_file)
            if ver:
                self.config["version"] = ver

    def setup(self):
        distutils.core.setup(**self.config)

cfgsetup = ConfigSetup(SETUP_CFG_FILE)
cfgsetup.configure()
cfgsetup.setup()
