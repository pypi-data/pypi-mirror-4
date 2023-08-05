from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '2.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('css', 'css3githubbuttons', 'test_css3_github_buttons.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='css.css3githubbuttons',
    version=version,
    description="Fanstatic packaging of CSS3 GitHub Buttons",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='fanstatic css3 buttons github',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    url='https://github.com/davidjb/css.css3githubbuttons',
    license='BSD',
    packages=find_packages(),namespace_packages=['css'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
    ],
    setup_requires=[
        'setuptools-git',
        'minify',
    ],
    entry_points={
        'fanstatic.libraries': [
            'css3_github_buttons = css.css3githubbuttons:library',
            ],
        },
    )
