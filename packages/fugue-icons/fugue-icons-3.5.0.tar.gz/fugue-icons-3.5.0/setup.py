from setuptools import setup

setup(
    name='fugue-icons',
    description='Fugue Icons packaged for simple use in web apps.',
    long_description="""
    Fugue Icons are created by Yusuke Kamiyamane
    <http://p.yusukekamiyamane.com/> and licensed under Creative Commons
    Attribution 3.0 <http://creativecommons.org/licenses/by/3.0/> license.
    This is a helper script and convenience packaging of those icons.
    The code is licensed under MIT license.
    """,
    version='3.5.0',
    license='MIT',
    author='Radomir Dopieralski',
    author_email='fugue@sheep.art.pl',
    url='https://bitbucket.org/thesheep/fugue-icons/',
    download_url='https://bitbucket.org/thesheep/fugue-icons/get/master.tar.gz',
    keywords='icon css sprite graphics ui',
    packages=['fugue_icons'],
    install_requires=['distribute'],
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ],
)
