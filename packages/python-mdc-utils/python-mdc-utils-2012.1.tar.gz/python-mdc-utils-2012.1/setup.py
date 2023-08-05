from distutils.core import setup


requires = [req.strip() for req in open('requirements.txt', 'r').readlines()]
long_desc = open('README.md', 'r').read()

setup(
    name="python-mdc-utils",
    version='2012.1',
    description="Automate exporting Mock Draft Central baseball ADP rankings",
    long_description=long_desc,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
    keywords='mockdraftcentral baseball data',
    author='Matt Dennewitz',
    author_email='mattdennewitz@gmail.com',
    url='https://github.com/mattdennewitz/mdc-utils/',
    license='BSD',
    packages=['mdc_utils'],
    install_requires=requires,
    scripts=['scripts/download-mdc-adp'],
    zip_safe=False,
)
