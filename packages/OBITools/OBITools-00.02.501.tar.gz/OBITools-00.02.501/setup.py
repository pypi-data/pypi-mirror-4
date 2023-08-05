#! /usr/bin/env python
#
# Install script
#
#


try:
   from setuptools.core import setup
except ImportError:
   from distutils.core import setup
from distutils.extension import Extension
from distutils.util import convert_path
from distutils import log
from distutils.dep_util import newer
from distutils import sysconfig

try:
    from Cython.Distutils import build_ext
    from Cython.Compiler import Main
    has_cython=True
except ImportError:
    from distutils.command.build_ext import build_ext
    has_cython=False

from distutils.command.build_scripts import build_scripts as ori_build_scripts
from distutils.command.build_scripts import first_line_re

from distutils.command.install_scripts import install_scripts as ori_install_scripts



from stat import ST_MODE

import os
import os.path
import re, sys
import glob

from os import path

class install_scripts(ori_install_scripts):

    def remove_deprecated_script(self):
        for f in DEPRECATED_SCRIPTS:
            try:
                ff = os.path.join(self.install_dir,f)
                os.unlink(ff)
                log.info('Removing deprecated unix command : %s (file : %s)' % (f,ff))
                ff = os.path.join(self.build_dir,f)
                os.unlink(ff)
            except:
                log.info('Unix command %s is not present' % f)
                pass

    def run(self):
        self.remove_deprecated_script()
        ori_install_scripts.run(self)
        

class build_scripts(ori_build_scripts):
            
    def copy_scripts (self):
        """Copy each script listed in 'self.scripts'; if it's marked as a
        Python script in the Unix way (first line matches 'first_line_re',
        ie. starts with "\#!" and contains "python"), then adjust the first
        line to refer to the current Python interpreter as we copy.
        """        
        self.mkpath(self.build_dir)
        rawbuild_dir = os.path.join(os.path.dirname(self.build_dir),'raw_scripts')
        self.mkpath(rawbuild_dir)
        
        outfiles = []
        for script in self.scripts:
            adjust = 0
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.splitext(os.path.basename(script))[0])
            rawoutfile = os.path.join(rawbuild_dir, os.path.basename(script))
            outfiles.append(outfile)

            if not self.force and not newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                continue

            # Always open the file, but ignore failures in dry-run mode --
            # that way, we'll get accurate feedback if we can read the
            # script.
            try:
                f = open(script, "r")
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn("%s is an empty file (skipping)" % script)
                    continue

                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ''
            
            log.info("Store the raw script %s -> %s", script,rawoutfile)        
            self.copy_file(script, rawoutfile)


            if adjust:
                log.info("copying and adjusting %s -> %s", script,
                         self.build_dir)
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not sysconfig.python_build:
                        outf.write("#!%s%s\n" %
                                   (self.executable,
                                    post_interp))
                    else:
                        outf.write("#!%s%s\n" %
                                   (os.path.join(
                            sysconfig.get_config_var("BINDIR"),
                           "python%s%s" % (sysconfig.get_config_var("VERSION"),
                                           sysconfig.get_config_var("EXE"))),
                                    post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            else:
                if f:
                    f.close()
                self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 07777
                    newmode = (oldmode | 0555) & 07777
                    if newmode != oldmode:
                        log.info("changing mode of %s from %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)
    
class build_filters(build_scripts):
    pass


def findPackage(root,base=None):
    modules=[]
    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
        modules.append('.'.join(base+[module]))
        modules.extend(findPackage(path.join(root,module),base+[module]))
    return modules
    
def findCython(root,base=None,pyrexs=None):
    modules=[]
    pyrexs=[]
    #o=dict(Main.default_options)
    pyopt=Main.CompilationOptions(Main.default_options)
    #print dir(pyopt)
    Main.__dict__['context'] = Main.Context(pyopt.include_path, {})
    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
                       
                
        for pyrex in glob.glob(path.join(root,module,'*.pyx')):
            pyrexs.append(Extension('.'.join(base+[module,path.splitext(path.basename(pyrex))[0]]),[pyrex]))
            pyrexs[-1].sources.extend(glob.glob(os.path.splitext(pyrex)[0]+'.ext.*.c'))
            print pyrexs[-1].sources
            Main.compile([pyrex],timestamps=True,recursion=True)
            
        pyrexs.extend(findCython(path.join(root,module),base+[module]))
    return pyrexs
    
def findC(root,base=None,pyrexs=None):
    modules=[]
    pyrexs=[]
    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
                
        for pyrex in glob.glob(path.join(root,module,'*.c')):
            if '.ext.' not in pyrex:
                pyrexs.append(Extension('.'.join(base+[module,path.splitext(path.basename(pyrex))[0]]),[pyrex]))
                pyrexs[-1].sources.extend(glob.glob(os.path.splitext(pyrex)[0]+'.ext.*.c'))
                print pyrexs[-1].sources
       
        pyrexs.extend(findC(path.join(root,module),base+[module]))
    return pyrexs
    

#sys.path.insert(0,"src")
#from obitools.version import version as obiversion
#sys.path.pop(0)

VERSION =  "00.02.501"
AUTHOR  = 'Eric Coissac'
EMAIL   = 'eric@coissac.eu'
URL     = 'www.grenoble.prabi.fr/trac/OBITools'
LICENSE = 'CeCILL-V2'

SRC       = 'src'
FILTERSRC = 'textwrangler/filter'

SCRIPTS = glob.glob('%s/*.py' % SRC)
FILTERS = glob.glob('%s/*.py' % FILTERSRC)

DEPRECATED_SCRIPTS=["fastaComplement", "fastaUniq","fasta2tab","fastaAnnotate",
                    "fastaSample","fastaGrep","fastaCount","fastaLength",
                    "fastaHead","fastaTail","fastaSplit","fastaStrand",
                    "fastaLocate","solexaPairEnd"
                   ]

def rootname(x):
    return os.path.splitext(x.sources[0])[0]

if  has_cython:
    EXTENTION=findCython(SRC)
    CEXTENTION=findC(SRC)
    cython_ext = set(rootname(x) for x in EXTENTION)
    EXTENTION.extend(x for x in CEXTENTION if rootname(x) not in cython_ext)
else:
    EXTENTION=findC(SRC)
    
#SCRIPTS.append('src/fastaComplement')

setup(name="OBITools",
      description="Scripts and library for sequence analysis",
      version=VERSION,
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      url=URL,
      scripts=SCRIPTS,
      package_dir = {'': SRC},
      packages=findPackage(SRC),
      cmdclass = {'build_ext': build_ext,'build_scripts':build_scripts, 'install_scripts':install_scripts},
      requires=['Cython (>=0.16)'],
      zip_safe = False,
      ext_modules=EXTENTION)

