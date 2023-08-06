try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='sphinx-patchqueue',
    version='0.2.1',
    py_modules=['patchqueue'],
    url='https://bitbucket.org/masklinn/sphinx-patchqueue',
    license='BSD',
    author='Xavier Morel',
    author_email='xavier.morel@masklinn.net',
    install_requires=['sphinx', 'mercurial'],
    description="Sphinx extension for embedding sequences of file alterations",
)
