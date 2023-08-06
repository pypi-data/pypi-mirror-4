from distutils.core import setup

setup(
    name='hyphenate_finnish',
    version='1.3.0',
    author='Pyry Kontio',
    author_email='pyry.kontio@drasa.eu',
    packages=['hyphenate_finnish'],
    scripts=[],
    url='http://pypi.python.org/pypi/hyphenate_finnish/',
    license='LGPL',
    description='A simple but working Finnish language hyphenator.',
    long_description=open('README.txt').read(),
    classifiers=[
    "Topic :: Text Processing :: Filters",
    "Topic :: Text Processing :: Linguistic",
    "Topic :: Internet :: WWW/HTTP",
    "Programming Language :: Python :: 3.3",
    "Natural Language :: Finnish",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    "Intended Audience :: Developers",
    "Development Status :: 4 - Beta",
    ]
)
