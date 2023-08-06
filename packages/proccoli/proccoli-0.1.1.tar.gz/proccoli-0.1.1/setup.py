from setuptools import setup

setup(
    name = 'proccoli',
    version = '0.1.1',
    description = 'Handy extensions for subprocess.Popen',
    author = 'Brian Lauber',
    author_email = 'constructible.truth@gmail.com',
    packages = ['proccoli'],
    install_requires = ['mock>=1.0'],
    test_suite = 'tests',
)

