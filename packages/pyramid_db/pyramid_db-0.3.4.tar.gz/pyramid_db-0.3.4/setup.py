from setuptools import setup

version = '0.3.4'

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
      description="SQLAlchemy, mongodb, redis, sqllite support for pyramid",
      classifiers=[],
      keywords='pymongo mongodb sqlalchemy redis sqllite pyramid',
      )
