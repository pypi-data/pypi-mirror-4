from setuptools import setup, find_packages


long_description = '\n\n'.join([open('README.rst').read(),
                                open('CHANGELOG.rst').read(),
                                open('TODO.rst').read()])


setup(
    name='gitchangelog',
    version='1.1.0',
    description='gitchangelog generates a changelog thanks to git log.',
    long_description=long_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Version Control",
        "Programming Language :: Python :: 2.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='sact git changelog',
    author='SecurActive SA',
    author_email='opensource@securactive.net',
    url='www.securactive.net',
    license='BSD License',
    py_modules=['gitchangelog'],
    namespace_packages=[],
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    [console_scripts]
    gitchangelog = gitchangelog:main
    """,
)
