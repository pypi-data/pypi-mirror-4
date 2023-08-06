from setuptools import setup

try:
    import pygtk
except ImportError:
    print 'You need to install pyGTK to use this'
    exit()

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='pyasteroids',
    version='0.5.3.rc1',
    description='Python asteroids game demonstrating pyagents library',
    long_description=readme(),
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    keywords='agent based asteroids',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment :: Arcade',
        'Environment :: X11 Applications :: GTK',
    ],
    url='https://github.com/ggstuart/pyasteroids.git',
    license='GPL',
    packages=[
        'pyasteroids'
    ],
    install_requires=[
        'pyagents'
    ],
    entry_points = {
        'console_scripts': ['pyasteroids=pyasteroids.command_line:main'],
    }
)
