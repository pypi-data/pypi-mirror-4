from setuptools import setup, find_packages

setup(
    name='context',
    version='0.0',
    description='A profiler that tells it how it is',
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Shish',
    author_email='shish+context@shishnet.org',
    url='http://code.shishnet.org/context',
    keywords='web syslog',
    packages=["context"],
    namespace_packages=["context"],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "context.api",
        "context.viewer",
    ],
)
