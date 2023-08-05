from distutils.core import setup

setup(
    name='CEPBR',
    version='0.1.0',
    author='Mauro Navarro Baraldi',
    author_email='mauro.baraldi@gmail.com',
    packages=['cepbr'],
    scripts=['cepbr/cep.py'],
    url='https://github.com/maurobaraldi/cepbr',
    license='LICENSE.txt',
    description='Biblioteca para acesso a base de CEP dos Correios do Brasil',
    long_description=open('README.txt').read(),
    py_modules=['cepbr'],
    install_requires=[],
)
