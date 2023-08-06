from distutils.core import setup

setup(
    name='hyphenate_finnish',
    version='1.1.1',
    author='Pyry Kontio',
    author_email='pyry.kontio@drasa.eu',
    packages=['hyphenate_finnish'],
    scripts=[],
    url='http://pypi.python.org/pypi/hyphenate_finnish/',
    license='LGPL',
    description='A simple but working Finnish language hyphenator.',
    long_description=open('README.txt').read(),
)
