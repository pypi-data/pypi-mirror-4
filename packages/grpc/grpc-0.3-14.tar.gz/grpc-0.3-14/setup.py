
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version_tuple = __import__('grpc').VERSION

if version_tuple[2] is not None:
    version = "%d.%d_%s" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

description = """Pure Python Gevent RPC
"""
setup(
    name = "grpc",
    version = version,
    url = 'https://bitbucket.org/seewind/grpc',
    author = 'seewind',
    author_email = 'seewindcn@gmail.com',
    description = description,
    license = "MIT",
    packages = ['grpc', 'grpc.test']
)
