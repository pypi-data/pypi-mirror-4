from setuptools import setup

setup(
    name = 'proccoli',
    version = '0.0.1',
    description = 'Handy extensions for subprocess.Popen',
    author = 'Brian Lauber',
    author_email = 'constructible.truth@gmail.com',
    packages = ['proccoli'],
    requires = ['mock (>=1.0)'],
    test_suite = 'tests',
)

