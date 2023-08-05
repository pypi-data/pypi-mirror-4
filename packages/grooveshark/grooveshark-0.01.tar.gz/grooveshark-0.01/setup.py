from setuptools import setup, find_packages
 
setup(
    name='grooveshark',
    version=__import__('grooveshark').__version__,
    description='Simple Grooveshark API Client',
    author='Luke Hutscal',
    author_email='luke@creaturecreative.com',
    url='http://github.com/girasquid/grooveshark/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    zip_safe=False,
)