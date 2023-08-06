from distutils.core import setup

setup(
    name = 'bwikibot',
    packages = ["bwikibot", 'bwikibot.extensions'],
    version = "0.4.2",
    description = "Simple mediawiki robot",
    author = "Taras Bunyk",
    author_email = "tbunyk@gmail.com",
    url = "http://code.google.com/p/bunykwikibot/",
    license='LICENSE.txt',
    #download_url = "link to tgz",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Internet :: WWW/HTTP",
    ],
    long_description = open('README.txt').read(),
    install_requires=[
        "httplib2 >= 0.7.0",
        "mwparserfromhell >= 0.1.1",
    ],
    entry_points=dict(console_scripts=[
        'bwikibot=bwikibot.cli:main',
    ]),
)
