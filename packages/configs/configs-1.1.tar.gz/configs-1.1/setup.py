from distutils.core import setup

setup(
    name='configs',
    version='1.1',
    description='Configuration for humans',
    author='Konstantin Molchanov',
    author_email='moigagoo@myopera.com',
    url='https://bitbucket.org/moigagoo/configs',
    py_modules=['configs'],
    data_files=[
        ('test', ['test.conf']),
    ],
    license='MIT'
)
