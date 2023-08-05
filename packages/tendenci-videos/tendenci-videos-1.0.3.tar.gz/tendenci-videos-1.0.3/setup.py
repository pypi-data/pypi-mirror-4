from setuptools import setup, find_packages

longdesc = \
'''
An addon for Tendenci for displaying embedded videos.
'''

setup(
    name='tendenci-videos',
    author='Schipul',
    author_email='programmers@schipul.com',
    version='1.0.3',
    license='GPL3',
    description='An addon for Tendenci for displaying embedded videos.',
    long_description=longdesc,
    url='https://github.com/tendenci/tendenci-videos',
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    packages=find_packages(),
    install_requires=['tendenci>=5.1'],
)
