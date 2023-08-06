Content links
=============

Content links is a `FeinCMS <http://www.feincms.org/>`_ `content type <http://feincms-django-cms.readthedocs.org/en/latest/contenttypes.html>`_ app which allows you to link other
FeinCMS pages, or external URLs, to specific page within your website.

Installation
============

1. Install it by

    pip install content-links


2. Add `content_links` to your `INSTALLED_APPS` in settings.py

    INSTALLED_APPS = (
        'awesome_app',

        'content_links',

        'django_stuff_etc',

    )

3. Register the app for FeinCMS in models.py

    from feincms.module.page.models import Page


    from content_links.models import ContentLink


    Page.create_content_type(ContentLink, TYPE_CHOICES=(
        ('one', 'One'),

        ('two', 'Two'),
        )

    )

4. Synchronize database by running

    python manage.py syncdb --all

5. Visit `admin panel <http://127.0.0.1:8000/admin/>`_ and have fun!
