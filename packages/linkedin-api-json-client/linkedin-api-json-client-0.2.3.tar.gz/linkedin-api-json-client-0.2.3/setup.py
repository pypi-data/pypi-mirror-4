import os, sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_deps():
    f = open(os.path.join(ROOT_DIR, "requirements.pip"), 'r')
    return [l[:-1] for l in f.readlines()]

# README is required for distribution, but README.md is required for github,
#   so create README temporarily
try:
    os.system('cp %s/README.md %s/README' % (ROOT_DIR, ROOT_DIR))
    copied_readme = True
except IOError:
    copied_readme = False

sdict = dict(
    name = 'linkedin-api-json-client',
    packages = ['linkedin_json_client'],
    version='.'.join(map(str, __import__('linkedin_json_client').__version__)),
    description = 'Python API for interacting with LinkedIn API.',
    long_description=open('README').read(),
    url = 'https://github.com/mattsnider/LinkedIn-API-JSON-Client',
    author = 'Matt Snider',
    author_email = 'admin@mattsnider.com',
    maintainer = 'Matt Snider',
    maintainer_email = 'admin@mattsnider.com',
    keywords = ['linkedin', 'api'],
    license = 'MIT',
    install_requires=get_deps(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)

from distutils.core import setup
setup(**sdict)

# cleanup README
if copied_readme:
    os.remove('%s/README' % ROOT_DIR)