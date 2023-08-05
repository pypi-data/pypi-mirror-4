from distutils.core import setup

setup(
    name='longdivision',
    version='0.1',
    author='Mantas Zimnickas',
    author_email='sirexas@gmail.com',
    py_modules=['longdivision'],
    url='https://bitbucket.org/sirex/longdivision',
    license='gpl.txt',
    description=('Script that breaks down a division problem into a series of '
                 'easier steps.'),
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
