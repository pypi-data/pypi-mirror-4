from setuptools import setup
import os.path


HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, 'README')) as f:
    ldesc = f.read()

setup(
        name='novaclient-auth-secretkey',
        version='0.1',
        author='fr33jc',
        author_email='fr33jc@gmail.com',
        packages=['novaclient_secretkey'],
        license='MIT',
        description=('Authentication plugin for novaclient enabling '
            'API key and secret key'),
        long_description=ldesc,
        platforms='POSIX',
        url='https://github.com/fr33jc/novaclient-auth-secretkey',
        install_requires=['python-novaclient'],
        entry_points={
            'openstack.client.authenticate': [
                'secretkey = novaclient_secretkey.auth_plugin:secretkey',
                ],
            },
        )
