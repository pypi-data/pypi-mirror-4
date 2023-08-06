from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this. Copied from Django's setup.py (https://github.com/django/django/blob/master/setup.py)
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)
 

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
project_dir = 'inoa'

for dirpath, dirnames, filenames in os.walk(project_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.') or dirname == '__pycache__':
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


setup(
    name='django-inoa',
    version='0.2.1',
    author='Inoa',
    author_email='django@inoa.com.br',
    packages=packages,
    data_files=data_files,
    scripts=[],
    url='https://bitbucket.org/inoa/django-inoa',
    license='LICENSE.txt',
    description='Collection of django tools and snippets commonly used by Inoa.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.3.1",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)