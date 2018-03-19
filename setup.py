from setuptools import setup, find_packages
import os
import SpiderMan


def read_file():
    with open('README.rst', encoding='utf-8') as f:
        return f.read()


def get_install_pack():
    with open('SpiderMan/requirements.txt', encoding='utf-8') as f:
        return [i.strip() for i in f.read().split() if i.strip()]


def package_files(dirs):
    paths = []
    for data in dirs:
        if os.path.isfile(os.path.abspath(data)):
            paths.append(os.path.abspath(data))
            continue
        for _path in os.walk(os.path.abspath(data)):
            [paths.append(os.path.join(_path[0], i)) for i in _path[2] if '.git' not in _path[0]]
    return paths


setup(
    name='SpiderMan',
    version=SpiderMan.version(),
    long_description=read_file(),
    description='Management of spiders based on scrapyd',
    keywords=['SpiderMan', 'scrapy', 'Distributed Management'],
    author='perror',
    email='perror_develop@sina.com',
    url="https://github.com/QYLGitHub/SpiderMan/tree/develop",
    install_requires=get_install_pack(),
    packages=find_packages(),
    entry_points={
        'console_scripts': ['SpiderMan = SpiderMan.Cmd:main']
    },
    package_data={
        '': package_files([
            'SpiderMan/server/web/templates/',
            'SpiderMan/',
            'SpiderMan/Cmd/',
        ])
    },
    publish=[
        'sudo python3 setup.py bdist_egg',
        'sudo python3 setup.py sdist',
        'sudo python3 setup.py bdist_egg upload'
        'sudo python3 setup.py sdist upload'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache-2.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
