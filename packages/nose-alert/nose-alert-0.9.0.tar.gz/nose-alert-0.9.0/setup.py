import nosealert
from setuptools import setup, find_packages


setup(
    name='nose-alert',
    version=nosealert.get_version(),
    author='Lukasz Balcerzak',
    author_email='lukaszbalcerzak@gmail.com',
    description=nosealert.__doc__,
    url='https://github.com/lukaszb/nose-alert',
    license = 'MIT',
    packages=find_packages(),
    package_data={'nosealert': ['images/*.png']},
    long_description=open('README.rst').read(),
    setup_requires=['nose>=1.0'],
    install_requires=['gntp>=0.9'],
    tests_require=['mock'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing',
    ],
    entry_points={
        'nose.plugins.0.10': [
            'alert = nosealert.plugin:AlertPlugin'
        ]
    }
)
