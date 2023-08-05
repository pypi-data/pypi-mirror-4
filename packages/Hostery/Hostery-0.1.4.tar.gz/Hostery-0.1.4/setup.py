from distutils.core import setup

setup(
    name='Hostery',
    version='0.1.4',
    author='George Michael Brower',
    author_email='george.brower@gmail.com',
    packages=['hostery'],
    package_dir={'hostery': 'hostery'},
    package_data={'hostery': ['*.tmpl']},
    scripts=['bin/hostery'],
    url='http://www.hostery.georgemichaelbrower.com/',
    license='LICENSE.txt',
    description='Pushes git snapshots to a webhost.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Jinja2 >= 2.5",
    ],
)
