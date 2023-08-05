from distutils.core import setup
setup(
    name='DQuery',
    version='0.0.1',
    author='David Gustafsson',
    author_email='david.gustafsson@xelera.se',
    packages=['dquery', 'dquery.commands', 'dquery.formatters', 'dquery.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/DQuery/',
    license='GPL',
    description='Drupal multisite query-tool.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PyYAML => 3.10",
        "SQLAlchemy => 0.7.8",
        "colorama => 0.2.4",
        "httplib2 => 0.7.6",
        "lxml => 3.0alpha2",
        "phpserialize => 1.3",
        "pyCLI => 2.0.3",
        "termcolor => 1.1.0",
    ],
)

