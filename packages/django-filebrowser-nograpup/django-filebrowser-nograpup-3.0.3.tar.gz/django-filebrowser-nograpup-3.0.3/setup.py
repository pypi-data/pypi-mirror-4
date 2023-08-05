from setuptools import setup, find_packages

setup(
    name='django-filebrowser-nograpup',
    version='3.0.3',
    description='Media-Management with the Django Admin-Interface.',
    author='Patrick Kranzlmueller',
    author_email='patrick@vonautomatisch.at',
    maintainer='Santiago Piccinini',
    maintainer_email="spiccinini@codigosur.org",
    url='https://github.com/spiccinini/django-filebrowser-no-grappelli-and-uploadify/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
