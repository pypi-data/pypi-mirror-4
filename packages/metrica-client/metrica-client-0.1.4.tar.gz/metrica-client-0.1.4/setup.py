from setuptools import setup


setup(name='metrica-client',
      version='0.1.4',
      scripts=['metrica_setup', 'metrica_connect'],
      install_requires=['pycrypto==2.6', 'requests==0.14.2'],
      description='Client to connect your database to the Metrica MongoDB Analytics service',
      url='http://getmetrica.com',
      author='David Crawford',
      author_email='david@getmetrica.com',
      license='MIT'
      )
