from setuptools import setup, find_packages

longdesc = \
'''
An addon for Tendenci for displaying embedded videos.

Supports Vimeo and YouTube embeds. Includes drag-n-drop reordering
in the Django admin area.
'''

setup(
    name='tendenci-videos',
    author='Schipul',
    author_email='programmers@schipul.com',
    version='1.0.4',
    license='GPL3',
    description='Videos addon for Tendenci',
    long_description=longdesc,
    url='https://github.com/tendenci/tendenci-videos',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    include_package_data=True,
    packages=find_packages(),
    install_requires=['tendenci>=5.1'],
)
