#!/bin/bash
# Push to pypi, tag and push to bitbucket

python setup.py sdist upload
rm -fr build dist
hg tag -f $(python setup.py --version)
hg push
