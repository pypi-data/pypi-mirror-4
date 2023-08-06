Release process
===============

* ensure changelog is up to date, features are documented that should be, etc
* update date in changelog
* update any packaging/ files to contain release dates and versions
* tag the release:  git tag -v X.Y
* make sdist
* upload tarball to ansible.cc/releases
* git checkout -b releaseX.Y
* git push --tags
* git push releaseX.Y origin/master
* update PyPi
* email the list
* blog post
* on devel branch, bump VERSION and packaging files and setup.py and __init__.py version
