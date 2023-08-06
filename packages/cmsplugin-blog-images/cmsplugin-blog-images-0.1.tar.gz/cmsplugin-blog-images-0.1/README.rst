cmsplugin-blog-images
=====================

An extension for `cmsplugin-blog <https://github.com/fivethreeo/cmsplugin-blog/>`_
which adds images to blog entries. This extension relies on django-filer.


Installation
------------

You need to install the following prerequisites in order to use this app::

    pip install Django
    pip install django-cms
    pip install cmsplugin-blog
    pip install django-filer
    pip install simple-translation

If you want to install the latest stable release from PyPi::

    $ pip install cmsplugin-blog-images

If you feel adventurous and want to install the latest commit from GitHub::

    $ pip install -e git://github.com/bitmazk/cmsplugin-blog-images.git#egg=cmsplugin_blog_images

Add ``cmsplugin_blog_images`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...,
        'cmsplugin_blog_images',
    )


Usage
-----

Just go to the ``Entry`` admin and you will see an inline admin to add images.


Templatetag: get_entry_images
+++++++++++++++++++++++++++++

In order to iterate over your blog entry's images, use the ``get_entry_images``
tag::

    {% load cmsplugin_blog_images_tags %}
    {% get_entry_images entry as entry_images %}
    {% for image in entry_images %}
        <img src="{{ image.image.url" />
    {% endfor %}


Contribute
----------

If you want to contribute to this project, please perform the following steps::

    # Fork this repository
    # Clone your fork
    $ mkvirtualenv -p python2.7 cmsplugin-blog-images
    $ pip install -r requirements.txt
    $ ./logger/tests/runtests.sh
    # You should get no failing tests

    $ git co -b feature_branch master
    # Implement your feature and tests
    # Describe your change in the CHANGELOG.txt
    $ git add . && git commit
    $ git push origin feature_branch
    # Send us a pull request for your feature branch

Whenever you run the tests a coverage output will be generated in
``tests/coverage/index.html``. When adding new features, please make sure that
you keep the coverage at 100%.


Roadmap
-------

Check the issue tracker on github for milestones and features to come.
