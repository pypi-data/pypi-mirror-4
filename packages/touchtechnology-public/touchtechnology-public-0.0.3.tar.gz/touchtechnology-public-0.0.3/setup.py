from distutils.core import setup
import os
import re


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

def pep386(v):
    regex = re.compile(r' (?:([ab])\w+) (\d+)$')
    if regex.search(v):
        base = regex.sub('', v)
        minor = ''.join(regex.search(v).groups())
        return base + minor
    return v


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
namespace = 'touchtechnology'

for dirpath, dirnames, filenames in os.walk(namespace):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files += [os.path.join(os.path.join(*fullsplit(dirpath)[2:]), f) for f in filenames]


version = __import__('touchtechnology.public', fromlist=['touchtechnology']).get_version()


setup(
    name = 'touchtechnology-public',
    version = pep386(version),
    url = 'http://www.touchtechnology.com.au/',
    author = 'Touch Technology Pty Ltd',
    author_email = 'support@touchtechnology.com.au',
    description = 'Publicly released components used in all Touch Technology library code.',
    install_requires = [
        'Django',
        ],
    extras_require = {},
    packages = packages,
    package_data = {'touchtechnology.public': data_files},
    namespace_packages = [namespace],
)
