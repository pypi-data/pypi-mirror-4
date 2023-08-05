from setuptools import setup

setup(
    name='dynconf',
    author='Jorge E. Cardona',
    description="Configuration file proxy.",
    author_email='jorgeecardona@gmail.com',
    version='0.3',
    packages=['dynconf'],
    entry_points = {
        'console_scripts': [
            'dynconf = dynconf.cli:main'
            ]}
    )
