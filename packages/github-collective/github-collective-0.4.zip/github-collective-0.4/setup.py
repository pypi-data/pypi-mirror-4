from setuptools import setup

version = '0.4'

setup(
    name='github-collective',
    version=version,
    description="Script to manage GitHub organizations in a collective manner",
    long_description=open("README.rst").read() + "\n" + \
                     open("docs/usage.rst").read() + "\n" + \
                     open("docs/etc.rst").read() + "\n" + \
                     open("CHANGES.rst").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        #"Programming Language :: Python :: 3.2",
        ],
    keywords='github git permission collaboration collective organization',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/collective/github-collective',
    license='BSD',
    packages=['githubcollective'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'setuptools-git',
    ],
    install_requires=[
        'argparse',
        'requests==0.13.1',
        ],
    extras_require={
        'test': ['nose'],
        'docs': ['Sphinx']
    },
    entry_points="""
        [console_scripts]
        github-collective = githubcollective:run
        """,
    )
