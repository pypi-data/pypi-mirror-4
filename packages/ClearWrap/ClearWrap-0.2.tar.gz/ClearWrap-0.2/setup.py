try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='ClearWrap',
    version='0.2',
    author='Andy MacKinlay',
    author_email='andrew.mackinlay@nicta.com.au ',
    url='https://bitbucket.org/nicta_biomed/clearwrap',
    packages=['clearwrap',],
    package_dir={'': 'src'},
    license='Apache 2.0',
    description='Wrapper for ClearParser',
    long_description=open('README.txt').read(),
    install_requires=['networkx >= 1.6'],
)
