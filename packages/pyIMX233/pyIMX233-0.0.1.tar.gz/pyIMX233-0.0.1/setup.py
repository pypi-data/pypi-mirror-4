from distutils.core import setup, Extension


setup(
    name                = 'pyIMX233',
    version             = '0.0.1',
    author              = 'LK',
    author_email        = 'luv4rice@ymail.com',
    url                 = 'https://www.olimex.com/',
    license             = 'MIT',
    description         = 'Control GPIOs on OLinuXino-Maxi.',
    long_description    = open('README.txt').read() + open('CHANGES.txt').read(),
    classifiers         = [ 'Development Status :: 3 - Alpha',
                            'Environment :: Console',
                            'Intended Audience :: Developers',
                            'Intended Audience :: Education',
                            'License :: OSI Approved :: MIT License',
                            'Operating System :: POSIX :: Linux',
                            'Programming Language :: Python',
                            'Programming Language :: Python :: 3',
                            'Topic :: Home Automation',
                            'Topic :: Software Development :: Embedded Systems'
          ],
    ext_modules         = [Extension('IMX233_GPIO', ['source/gpio_lib.c', 'source/pyIMX233.c'])],
    package_dir={'': 'source'},
    packages=[''],
  
                            
)
