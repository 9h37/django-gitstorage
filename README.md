django-gitstorage
=================

Django Storage backend built on top of pygit2.

## Usage

    #!python
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
