=====================
Django Sublime Scroll
=====================
"Sublime Text 2"-style scroll bars.


Installation:
=============
* pip install django-sublime-scroll

* Setup wkhtmltoimage

* load template tags
.. code:: jinja

    {% load sublime_scroll_tags %}
    {% sublime_scroll %}

* It's a good idea to have some cache so that the page capture is not generated every time that the page is loaded. So at the very least, you should do this:

.. code:: jinja

    {% load sublime_scroll_tags cache %}
    {% cache 500 sublime_scroll %}
        {% sublime_scroll %}
    {% endcache %}

* Make sure to include RequestContext in response. Example:

.. code:: python

    from django.template import RequestContext        
    return render_to_response('index.html', {'form': form, }, 
                              context_instance = RequestContext(request))


Settings:
=========
.. code:: python

    # Absolute path to wkhtmltoimage if not in system PATH:
    SUBLIME_SCROLL_WKHTMLTOIMAGE_PATH # (default: "wkhtmltoimage")

    # Scroll Bar width:
    SUBLIME_SCROLL_SETTINGS
    # Default (in javascript):
    {
        'scroll_width': 150,
        'offset': 0,
        'z_index': 50,
        'content_width': 960,
        'full_height': "$('html').height()",
        'opacity': 0.1,
        'color': 'white',
    }

