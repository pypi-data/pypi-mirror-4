from setuptools import setup, find_packages

setup(
    name='django-staticfiles-jquery-ui',
    version='1.8.24',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,

    setup_requires=['hgtools >=2, <2.1'],
    install_requires=[
        'Django',
    ],

    description='jquery-ui packaged for django-staticfiles',

    author='Rohan de Swardt',
    author_email='rohanza@gmail.com',

    maintainer='Byte Orbit',
    maintainer_email='admin@byteorbit.com',
    url='http://byteorbit.com/',
    license='BSD',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
