After syncdb's signal is called, root user is created (if not exists).
Default settings creates root:root@localhost:qqq user, but
you can customize it in settings by::

    AUTOROOT_NAME
    AUTOROOT_EMAIL
    AUTOROOT_PASSWORD


You can tell to create superuser only in DEBUG mode by changing variable below,
in `settings.py`::

    AUTOROOT_DEBUG_ONLY (default True)


Code is stolen from:
http://djangosnippets.org/snippets/1875/
