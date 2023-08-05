try:
    from setuptools import setup, find_packages
except ImporterError:
    from ez_setup import use_setuptools #@UnresolvedImport
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='ssrf',
    version='0.1.0',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    license='Creative Commons Attribution-Share Alike license',
    long_description=open('README.md').read(),
    install_requires=[],
    tests_require=['nose', 'mox'],
    author='Adam Dziendziel',
    author_email='adam.dziendziel@gmail.com',
    url='https://github.com/AdamDz/ssrf-python',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
    ],
)

