Translations
============

Rebuild POT:

.. code-block:: sh

    $ i18ndude rebuild-pot --pot locales/iwwb.eventlist.pot --create iwwb.eventlist .

Sync a translation file with POT:

.. code-block:: sh

    $ find locales -name '*.po' -exec i18ndude sync --pot locales/iwwb.eventlist.pot {} \;

