from setuptools import setup, find_packages

longdesc = \
    """
    An addon for Tendenci for displaying staff.
    """

setup(
    name='tendenci-staff',
    author='Schipul',
    author_email='programmers@schipul.com',
    version='1.0.3',
    license='GPL3',
    description='Staff addon for Tendenci',
    long_description=longdesc,
    url='https://github.com/tendenci/tendenci-staff',
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
