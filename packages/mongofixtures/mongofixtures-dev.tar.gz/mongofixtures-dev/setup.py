from setuptools import find_packages, setup


version = 'dev'

setup(
    name='mongofixtures',
    version=version,
    description='Fixtures for MongoDB',
    #packages=['mongofixtures'],
    packages=find_packages('src'),
    author='Rodrigo Machado',
    author_email='rcmachado@gmail.com',
    url='https://github.com/rcmachado/mongofixtures',
    keywords=['mongo', 'fixtures'],
    package_dir={'mongofixtures': 'src/mongofixtures'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Testing',
    ]
)
