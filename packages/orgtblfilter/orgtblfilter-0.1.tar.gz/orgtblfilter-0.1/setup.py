from setuptools import setup, find_packages


setup(
    name = "orgtblfilter",
    version = "0.1",
    packages = find_packages(),
    author = "Diez B. Roggisch",
    author_email = "deets@web.de",
    description = "A sphinx extension to pre-process orgtbl-mode tables to sphinx tables",
    license = "BSD",
    url="https://github.com/deets/orgtblfilter",
    requires=["sphinx"],
    keywords = "sphinx extension",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],    
    entry_points = {
        'console_scripts': [
        ],
    }    
)

