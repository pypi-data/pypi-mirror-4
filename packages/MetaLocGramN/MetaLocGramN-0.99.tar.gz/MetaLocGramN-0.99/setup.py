from setuptools import setup, find_packages

setup(
    name='MetaLocGramN',
    version='0.99',
    description="MetaLocGramN: a method for subcellular localization prediction of Gram-negative proteins.",
    #long_description=get_long_description(),
    keywords='bioinformatics, subcellular localization, prediction, gram-negative, sequence, analysis',
    author='Magnus Marcin, Pawlowski Marcin, Bujnicki Janusz M',
    author_email='magnus@genesilico.pl',
    url='http://iimcb.genesilico.pl/MetaLocGramN/home',
    license='GPLv3',
    py_modules=['MetaLocGramN','test'],

    zip_safe=False,
    install_requires=[
        'suds>=0.04',
    ],
    classifiers=[
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Environment :: Console",
    ],
    )
