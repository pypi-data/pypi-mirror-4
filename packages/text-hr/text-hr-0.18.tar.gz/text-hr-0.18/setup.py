# coding=utf-8
from distutils.core import setup
from codecs import open

files = ["text_hr/std_words.txt"]
long_description = open("README", "r", "utf-8").read().encode("utf-8")

setup(
    name='text-hr',
    version='0.18',
    #Name the folder where your packages live:
    packages = ['text_hr'],
    #'package' package must contain files (see list above)
    #It says, package *needs* these files.
    package_data = {'text_hr' : files },
    description = "Morphological/Inflection/Lemmatization Engine for Croatian language, POS tagger, stopwords",
    author = "Robert Lujo",
    author_email = "trebor74hr@gmail.com",
    url = "http://bitbucket.org/trebor74hr/text-hr/",
    #'runner' is in the root.
    # scripts = ["runner"],
    long_description = long_description,
    # TODO: enable hr chars in char before

    # This next part it for the Cheese Shop
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Croatian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Text Processing',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Indexing',
      ]
    )


