try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='StructuRX',
    version='0.2',
    author='Andrew MacKinlay',
    author_email='andrew.mackinlay@nicta.com.au',
    packages=['structurx',],
    package_dir={'': 'src'},
    scripts=['bin/structurx-run.py'],
    license='Apache 2.0',
    url='http://opennicta.com/home/structurx',
    download_url='https://bitbucket.org/nicta_biomed/structurx/downloads',
    description='Interpret medication prescriptions into a structured '
        'format using dependency parses or third-party drug NER pipeline',
    long_description=open('README.txt').read(),
    zip_safe=True,
    install_requires=['ClearWrap >= 0.2'],
)
