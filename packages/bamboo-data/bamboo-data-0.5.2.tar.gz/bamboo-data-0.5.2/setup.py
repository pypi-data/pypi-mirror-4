from distutils.core import setup

setup(
     name='bamboo-data',
     version='0.5.2',
     author='Modi Research Group',
     author_email='info@modilabs.org',
     packages=['bamboo'],
     package_dir={'bamboo': 'bamboo'},
     url='http://pypi.python.org/pypi/bamboo/',
     description='Dynamic data analysis over the web. The logic to your data '
                 'dashboards.',
     long_description=open('README.rst', 'rt').read(),
     install_requires=[
        # celery requires python-dateutil>=1.5,<2.0
        'python-dateutil==1.5',

        # for pandas
        'numpy',
        'pandas',
        'scipy',

        # for celery
        'kombu',
        'celery',
        'pymongo',

        'cherrypy',
        'pyparsing',
        'simplejson',
        'Routes'
    ],
)
