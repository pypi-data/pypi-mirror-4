from distutils.core import setup, Extension

fsdir_mod = Extension('fsdir', sources = ['src/crc32.c','src/fsdir.c'])

setup (name = 'fsdir',
       version = '0.8',
       description = 'File System Scan',
       url= "https://fsdir.googlecode.com",
       author="Rui Gomes",
       author_email="rui.tech@gmail.com",
       license = "GPL v2",
       platforms = "*nix/OSx",
       ext_modules=[fsdir_mod])
