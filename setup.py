from io import open
from os.path import join, dirname

from setuptools import setup, find_packages
import gps2nextcloud

setup(
    name='gps2nextcloud',
    version=gps2nextcloud.__version__,
    packages=find_packages(),
    url='https://github.com/AlexanderBekrenev/gps2nextcloud',
    license='MIT',
    author='Alexander Bekrenev',
    author_email='alexander.bekrenev@gmail.com',
    description='Simple gate between TCP tracker sessions and Nextcloud PhoneTrack',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    entry_points={
        'console_scripts':
            [
                 'gps2nextcloud-install =  gps2nextcloud.server_config:create_daemon'
             ]
        },
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    python_requires='>=3',
    install_requires=['requests', 'numpy', 'scipy', 'pyproj']
)
