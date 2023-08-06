Installation
===========

1. Install ralph_assets package from pypi by running: ``pip install ralph_assets``

2. After installation add line to the end of INSTALLED_APPS

::

    INSTALLED_APPS += (
    ...
    'ralph_assets'
    )

3. Run: 
``ralph migrate``

That's it. Now just run ralph as described in ralph documentation, and login to the Ralph system. 
Menu item called 'assets' will be shown to you on the main menu bar.

