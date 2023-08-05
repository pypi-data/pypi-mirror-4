from setuptools import setup, find_packages

setup(
    name="prat-geventwebsocket",
    version="0.3.7",
    description="Prat fork of Jeffrey Gelen's gevent Websocket handler",
    long_description=open("README.rst").read(),
    author="Kevin Le",
    author_email="solnovus@gmail.com",
    license="BSD",
    url="https://github.com/bkad/gevent-websocket",
    download_url="https://github.com/bkad/gevent-websocket",
    install_requires=("prat-gevent", "greenlet"),
    packages=find_packages(exclude=["examples","tests"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
)
