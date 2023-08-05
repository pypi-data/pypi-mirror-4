#!/usr/bin/env python
import os.path
import re
import sys
import tempfile
import zipfile
import wheel.bdist_wheel
import distutils.dist
from distutils.archive_util import make_archive
from shutil import rmtree
from wheel.archive import archive_wheelfile

egg_info_re = re.compile(r'''(^|/)(?P<name>[^/]+?)-(?P<ver>.+?)
    (-(?P<pyver>.+?))?(-(?P<arch>.+?))?.egg-info(/|$)''', re.VERBOSE)

def parse_info(wininfo_name, egginfo_name):
    """Extract metadata from filenames.
    
    Extracts the 4 metadataitems needed (name, version, pyversion, arch) from
    the installer filename and the name of the egg-info directory embedded in
    the zipfile (if any).

    The egginfo filename has the format
        name-ver(-pyver)(-arch).egg-info
    The installer filename has the format
        name-ver.arch(-pyver).exe

    Some things to note:
    1. The installer filename is not definitive. An installer can be renamed
       and work perfectly well as an installer. So more reliable data should
       be used whenever possible.
    2. The egg-info data should be preferred for the name and version, because
       these come straight from the distutils metadata, and are mandatory.
    3. The pyver from the egg-info data should be ignored, as it is
       constructed from the version of Python used to build the installer,
       which is irrelevant - the installer filename is correct here (even to
       the point that when it's not there, any version is implied).
    4. The architecture must be taken from the installer filename, as it is
       not included in the egg-info data.
    """

    egginfo = None
    if egginfo_name:
        egginfo = egg_info_re.search(egginfo_name)
        if not egginfo:
            raise ValueError("Egg info filename %s is not valid" %
                    (egginfo_name,))

    # Parse the wininst filename
    # 1. Distribution name (up to the first '-')
    w_name, sep, rest = wininfo_name.partition('-')
    if not sep:
        raise ValueError("Installer filename %s is not valid" %
                (wininfo_name,))
    # Strip '.exe'
    rest = rest[:-4]
    # 2. Python version (from the last '-', must start with 'py')
    rest2, sep, w_pyver = rest.rpartition('-')
    if sep and w_pyver.startswith('py'):
        rest = rest2
    else:
        # Should be 'any' but wheel format doesn't support this...
        w_pyver = 'py9.9' # Dummy to see what happens...
    # 3. Version and architecture
    w_ver, sep, w_arch = rest.rpartition('.')
    if not sep:
        raise ValueError("Installer filename %s is not valid" %
                (wininfo_name,))

    if egginfo:
        w_name = egginfo.group('name')
        w_ver = egginfo.group('ver')

    return dict(name=w_name, ver=w_ver, arch=w_arch, pyver=w_pyver)

def bdist_wininst2wheel(path):
    bdw = zipfile.ZipFile(path)

    # Search for egg-info in the archive
    egginfo_name = None
    for filename in bdw.namelist():
        if '.egg-info' in filename:
            egginfo_name = filename
            break

    info = parse_info(os.path.basename(path), egginfo_name)

    root_is_purelib = True
    for zipinfo in bdw.infolist():
        if zipinfo.filename.startswith('PLATLIB'):
            root_is_purelib = False
            break
    if root_is_purelib:
        paths = {'purelib': ''}
    else:
        paths = {'platlib': ''}

    dist_info = "%(name)s-%(ver)s" % info
    datadir = "%s.data/" % dist_info

    # rewrite paths to trick ZipFile into extracting an egg
    # XXX grab wininst .ini - between .exe, padding, and first zip file.
    members = []
    egginfo_name = ''
    for zipinfo in bdw.infolist():
        key, basename = zipinfo.filename.split('/', 1)
        key = key.lower()
        basepath = paths.get(key, None)
        if basepath is None:
            basepath = datadir + key.lower() + '/'
        oldname = zipinfo.filename
        newname = basepath + basename
        zipinfo.filename = newname
        del bdw.NameToInfo[oldname]
        bdw.NameToInfo[newname] = zipinfo
        # Collect member names, but omit '' (from an entry like "PLATLIB/"
        if newname:
            members.append(newname)
        # Remember egg-info name for the egg2dist call below
        if not egginfo_name:
            if newname.endswith('.egg-info'):
                egginfo_name = newname
            elif '.egg-info/' in newname:
                egginfo_name, sep, _ = newname.rpartition('/')
    dir = tempfile.mkdtemp(suffix="_b2w")
    bdw.extractall(dir, members)

    # egg2wheel
    abi = 'none'
    pyver = info['pyver'].replace('.', '')
    arch = (info['arch'] or 'any').replace('.', '_').replace('-', '_')
    if arch != 'any':
        # assume all binary eggs are for CPython
        pyver = 'cp' + pyver[2:]
    wheel_name = '-'.join((
                          dist_info,
                          pyver,
                          abi,
                          arch
                          ))
    bw = wheel.bdist_wheel.bdist_wheel(distutils.dist.Distribution())
    bw.root_is_purelib = root_is_purelib
    dist_info_dir = os.path.join(dir, '%s.dist-info' % dist_info)
    bw.egg2dist(os.path.join(dir, egginfo_name), dist_info_dir)
    bw.write_wheelfile(dist_info_dir, generator='egg2wheel')
    bw.write_record(dir, dist_info_dir)
    
    archive_wheelfile(wheel_name, dir)
    rmtree(dir)

def main():
    bdist_wininst2wheel(sys.argv[1])

if __name__ == "__main__":
    main()
