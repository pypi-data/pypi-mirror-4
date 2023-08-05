Eventlet_inotifyx -- Damn simple wrapper
========================================

About
-----

Wrapper around inotifyx to use with eventlet, call to ``get_events`` will block only current eventlet.
Thanks to Stanis Trendelenburg (@trendels) for `gevent_inotifyx <https://github.com/trendels/gevent_inotifyx>`_.

API
---

See `Inotifyx <http://www.alittletooquiet.net/software/inotifyx/>`_ for more info.

Usage
-----

::
    import eventlet_inotifyx as inotifyx

    fd = inotifyx.init()
    fd.add_watch(fd, path)
    events = inotifyx.get_events()


Install
-------

~/yourvirtualenv/python setup.py install

pip install eventlet_inotifyx

License
-------

The MIT License, in LICENSE file.
