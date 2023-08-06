from setuptools import setup, find_packages

__version__ = '0.9'

setup(
    name='zope.z2release',
    version=__version__,
    description="Zope release helper",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.rst").read()),
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='',
    author='Zope Foundation',
    author_email='zope-dev@zope.org',
    url='http://pypi.python.org/pypi/zope.z2release',
    license='ZPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points=dict(console_scripts=[
        'z2_kgs=zope.z2release.cli:main',
        'ztk_kgs=zope.z2release.ztk:main'
    ]),
)
