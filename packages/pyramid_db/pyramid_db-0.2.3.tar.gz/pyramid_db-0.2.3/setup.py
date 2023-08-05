from setuptools import setup

version = '0.2.3'

install_requires = [
    'pyramid',
    'sqlalchemy',
    'pymongo',
    'redis',
    ]
    
setup(
      name='pyramid_db',
      version=version,
      author='DreadNought',
      author_email='DreadNought.team@gmail.com',
      install_requires = install_requires,
      description="SQLAlchemy, mongodb, redis, support for pyramid",
      classifiers=[],
      keywords='pymongo mongodb sqlalchemy redis pyramid',
      )
