from distutils.core import setup

setup(
  name='PyOPC',
  version='0.1a',
  author='Hermann Himmelbauer',
  packages=['PyOPC','PyOPC.test','PyOPC.samples','PyOPC.samples.clients','PyOPC.samples.ESD','PyOPC.samples.simple_server','PyOPC.servers','PyOPC.protocols','PyOPC.wsdl'],
  url='http://pyopc.sourceforge.net/',
  license='LICENSE.txt',
  description='Python OPC-DA XML Twisted Server',
  long_description=open('README.txt').read(),
  install_requires=[
    'ZSI >= 2.0-rc3',
    'Twisted >= 12.2.0',
  ],
)
