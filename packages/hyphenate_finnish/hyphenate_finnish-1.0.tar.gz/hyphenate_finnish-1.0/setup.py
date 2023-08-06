from distutils.core import setup

setup(
    name='hyphenate_finnish',
    version='1.0',
    author='Pyry Kontio',
    author_email='pyry.kontio@drasa.eu',
    packages=['hyphenate_finnish'],
    scripts=[],
    url='http://pypi.python.org/pypi/hyphenate_finnish/',
    license='LICENSE.txt',
    description='A simple but working Finnish language hyphenator.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
