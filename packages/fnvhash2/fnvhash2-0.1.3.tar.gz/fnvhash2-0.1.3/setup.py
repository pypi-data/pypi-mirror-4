from distutils.core import setup, Extension

module1 = Extension('fnvhash2',
                    sources = ['fnvhash2.c','hash_32a.c','hash_32.c','hash_64.c','hash_64a.c'])

setup (name = 'fnvhash2',
       version = '0.1.3',
       description = 'Python extension for FNV Hash Algorithms',
       classifiers=[
        "Programming Language :: Python",],
       keywords='FNV Hash',
       author='Seimei',
       author_email='seimeininja@gmail.com',
       url='http://github.com/seimei/python-fnvhash2',
       license='BSD',
       ext_modules = [module1])
