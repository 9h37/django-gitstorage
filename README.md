django-gitstorage
=================

Django Storage backend built on top of pygit2.

## Usage

    from gitstorage.StorageBackend import GitStorage
    from django.contrib.auth.models import User
    
    u = User()
    u.first_name = u'David'
    u.last_name = u'Delassus'
    u.email = 'david.delassus@9h37.fr'

    r = GitStorage.create_storage('test')

    f = r.open('test/test.txt', mode='w')
    f.write('this is a file\n')
    f.close()

    r.commit(u, 'test commit')

## Installation

    $ ./venv.sh
    $ . .venv/bin/activate
    $ python setup.py install

Or to update :

    $ ./venv.sh update
    $ . .venv/bin/activate
    $ python setup.py install

## Running the test suite

    $ . .venv/bin/activate
    $ cd tests && ./test.sh

[![Build Status](https://travis-ci.org/linkdd/django-gitstorage.png?branch=master)](https://travis-ci.org/linkdd/django-gitstorage)
