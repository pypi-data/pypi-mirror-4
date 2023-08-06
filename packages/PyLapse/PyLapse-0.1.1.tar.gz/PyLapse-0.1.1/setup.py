import os
from distutils.core import setup

HOME_PATH = os.path.expanduser('~')
CONFIG_PATH = '%s/.pylapse' % HOME_PATH

setup(
    name='PyLapse',
    version='0.1.1',
    author='Javier Aguirre',
    author_email='contacto@javaguirre.net',
    packages=['pylapse'],
    scripts=['bin/pylapse'],
    data_files=[(CONFIG_PATH, ['data/config.cfg']),
                ('/'.join([CONFIG_PATH, 'captures']), []),
                ('/'.join([CONFIG_PATH, 'videos']), [])
                ],
    url='https://github.com/javaguirre/pylapse',
    license=open('LICENSE.txt').read(),
    description='A simple application to build timelapses using a webcam, V4l2 and ImageMagick',
    long_description=open('README.txt').read(),
    install_requires=['PIL == 1.1.7',
                      'v4l2 == 0.2',
                      'v4l2capture == 1.4']
)
