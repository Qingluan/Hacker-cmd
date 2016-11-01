

from setuptools import setup, find_packages


setup(name='hackcmds',
    version='0.1',
    description='a simple way to use mongo db, let db like dict',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['Mroylib'],
    entry_points={
        'console_scripts': ['Hacker=Hacker.cmd:main']
    },

)


