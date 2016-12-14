

from setuptools import setup, find_packages


setup(name='hackcmds',
    version='4.8',
    description='add auto analyzer for txt',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['mroylib-min','reportlab'],
    include_package_data=True,
    entry_points={
        'console_scripts': ['Hacker=Hacker.libs.cmd:main']
    },
		scripts = [
        'init.sh'
    ]

)


