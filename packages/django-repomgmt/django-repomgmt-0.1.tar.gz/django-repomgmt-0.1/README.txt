python-django-repomgmt

This Django app implements everything you need to create APT repositories,
buildd infrastructure as well as automatic package building.

It expects access to an OpenStack Compute cloud to perform builds and uses
reprepro on the backend to manage the APT repositories, process incoming,
etc.

Setting it up should be fairly simple.
