Pyramid machinery for TinyMCE spellchecker ajax calls. Currently only supports Enchant backend.

INSTALL
=======

::

    $ pip install pyramid_tinymce_spellchecker


USAGE
=====

Use pyramid addon that will configure an ajax view::

    config.include('pyramid_tinymce_spellchecker')

Configure TinyMCE to use spellchecker::

    tinyMCE.init({
        ...
        theme: "advanced",
        plugins: "spellchecker",
        theme_advanced_buttons3_add: "spellchecker",
        spellchecker_languages = '+English=en',
        spellchecker_rpc_url = '{{ request.route_url('tinymce_spellchecker') }}',
        ...
    })

(for options see http://www.tinymce.com/wiki.php/Plugin:spellchecker)


DEVELOP
=======

::

    $ git clone https://github.com/iElectric/pyramid_tinymce_spellchecker pyramid_tinymce_spellchecker
    $ cd pyramid_tinymce_spellchecker
    $ virtualenv .
    $ source bin/activate
    $ python setup.py dev


RUNNING TESTS
=============

::

    $ make
