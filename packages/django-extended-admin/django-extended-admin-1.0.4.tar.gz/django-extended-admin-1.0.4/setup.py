import os
from distutils.core import setup

name = 'django-extended-admin'
inner_dir = 'admin_extended'

version = __import__(inner_dir).__version__
bitbucket_url = "http://bitbucket.org/masterzeb/%s/" % name
packages, data_files = [], []


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), 'README')).read()


for dirpath, dirnames, filenames in os.walk(inner_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[(len(inner_dir) + 1):]
        for file_name in filenames:
            data_files.append(os.path.join(prefix, file_name))

setup(
    name=name,
    version=version,
    author='Denis Savasteev',
    author_email='devmaster.zeb@gmail.com',
    description='Additional features for django admin',
    long_description=read('README'),
    license="BSD",

    packages=packages,
    package_dir={inner_dir: inner_dir},
    package_data={inner_dir: data_files},

    url=bitbucket_url,
    download_url='%sdownloads/%s-%s.tar.gz' % (bitbucket_url, name, version),

    install_requires=['django >= 1.5.1', 'django-apptemplates'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django']
)
