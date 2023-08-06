from distutils.core import setup, Extension


classifiers = [ 'Development Status :: 1 - Planning',
                'Intended Audience :: Developers',
                'Programming Landuage :: Python :: 2.6',
                'Programming Landuage :: Python :: 2.7',
                'Programming Landuage :: Python :: 3',
                'Topic :: Software Development',
                'Topic :: Home Automation',
                'Topic :: System',
                'Topic :: Hardware']
                

setup(
    name                = 'pyA13',
    version             = '0.1.5',
    author              = 'Stefan Mavrodiev',
    author_email        = 'support@olimex.com',
    packages            = ['pyA13', 'pyA13.test'],
    url                 = 'https://www.olimex.com/',
    license             = 'LICENSE.txt',
    description         = 'Control GPIOs on OLinuXino-A13.',
    long_description    = open('README.txt').read() + open('CHANGES.txt').read(),
    ext_modules         = [Extension('A13_GPIO', ['source/gpio_lib.c', 'source/pyA13.c'])])
