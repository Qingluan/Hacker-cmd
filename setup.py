

from setuptools import setup, find_packages


setup(name='hackcmds',
    version='3.8',
    description='add social db',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['mroylib-min'],
    include_package_data=True,
    entry_points={
        'console_scripts': ['Hacker=Hacker.libs.cmd:main']
    },
		scripts = [
        'init.sh'
    ]

)


