from distutils.core import setup
VERSION = '0.1'

setup(name='kloc',
        version=VERSION, 
        author='Zhang Zhihong',
        author_email='zzh10000@gmail.com',
	py_modules = ['kloc'],
	url='http://www.zzh.com',
        description='A tool to count lines of code',
        license='MIT',
        long_description='A tool to count lines of code',
        classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'        
        ]
        )
