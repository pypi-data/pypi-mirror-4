import os

from setuptools import setup

install_requires = []

README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README')

description = 'Django specific cookie implementation compliant with Dutch law, use at your own risk.'

if os.path.exists(README_PATH):
    long_description = open(README_PATH).read()
else:
    long_description = description

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('cookie_law'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[11:] # Strip "cookie_law/"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))



setup(
    name='django-cookie-law-nl',
    version='0.1.5',
    install_requires=install_requires,
    include_package_data=True,
    description=description,
    long_description=long_description,
    author='Wouter Lansu',
    author_email='wfrlansu@gmail.com',
    url='https://bitbucket.org/getlogic/lib_django_cookie_law',
    packages=packages,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
)
