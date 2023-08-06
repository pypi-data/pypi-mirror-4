from distutils.core import setup
setup(
    name='taffmat',
    version='0.1.1',
    author='Matthew Rankin',
    author_email='matthew@questrail.com',
    py_modules=['taffmat'],
    url='http://github.com/questrail/taffmat',
    license='LICENSE.txt',
    description='Read and write Teac TAFFmat files.',
    long_description=open('README.rst').read(),
    requires=['numpy (>=1.6.0)'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
