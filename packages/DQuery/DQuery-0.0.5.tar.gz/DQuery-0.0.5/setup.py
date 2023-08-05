from setuptools import setup, find_packages
setup(
    name='DQuery',
    version='0.0.5',
    author='David Gustafsson',
    author_email='david.gustafsson@xelera.se',
    packages=['dquery', 'dquery.commands', 'dquery.formatters', 'dquery.test'],
    #packages=find_packages(),
    data_files={'dquery' : ['json_settings.php']},
    scripts=['bin/php_var_json', 'bin/dquery'],
    url='http://pypi.python.org/pypi/DQuery/',
    license='GPL',
    description='Drupal multisite query-tool.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PyYAML",
        "SQLAlchemy",
        "colorama",
        "httplib2",
        "lxml",
        "phpserialize",
        "pyCLI",
        "termcolor",
    ],
)

