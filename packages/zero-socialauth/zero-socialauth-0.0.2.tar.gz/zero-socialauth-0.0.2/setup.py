from setuptools import find_packages, setup


setup(
    # Basic package information:
    name = 'zero-socialauth',
    version = '0.0.2',
    packages = ['socialauth'],
    
    # Packaging options:
    zip_safe = False,
    include_package_data = True,
    
    # Package dependencies:
    install_requires = ['zero-common>=0.1.2', 'Django>=1.3.1', 'South>=0.7.3'],
    
    # Metadata for PyPI:
    author = 'Jose Maria Zambrana Arze',
    author_email = 'contact@josezambrana.com',
    license = 'apache license v2.0',
    url = 'http://github.com/josezambrana/Zero-Socialauth',
    keywords = 'zero socialauth social',
    description = 'Simple app to add social authentication in django projects',
    long_description = "Simple app to add social authentication in django projects"
)

