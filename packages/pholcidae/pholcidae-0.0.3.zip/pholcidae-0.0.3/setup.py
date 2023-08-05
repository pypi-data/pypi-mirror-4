from distutils.core import setup

setup(
    name = 'pholcidae',
    packages = ['pholcidae'],
    version = '0.0.3',
    description = 'pholcidae - Tiny python web crawler library',
    author = 'bender.rodriges',
    author_email='bender@rodriges.org',
    url = 'https://github.com/bbrodriges/pholcidae',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],
    long_description=open('README.txt').read(),
)