Note
====

This is a demo created for documentation purpose.

Goal
====

block_generator
----------------

- Extract `item-data` from the website of [Path Of Exile](http://www.pathofexile.com) game by Grinding Gear Games
- Generate Awakening compatible loot filter Show blocks for crossed requirements (ie. STR/DEX, INT... in `item-data/armour`)
- Compress item names in list by checking there's no name conflict with other databases (weapons, currency, jewelry...)

simple_loot_fixer
-----------------

- replace every Smartblock header's changes in [antnee](http://www.pathofexile.com/forum/view-thread/1245785) loot filter or any other filters using a Smartblocks convention

Requirement
===========

- Python 3.3+ (Python 3.4 is highly recommended; tested on 3.4.3)
- [pip](https://pypi.python.org/pypi/pip) (included in python 3.4+); install this module via the command `python get-pip.py` after having installed [Setuptools](http://pypi.python.org/pypi/setuptools)
- BeautifulSoup (for classy_generator)
- Pygments 2.0 (for classy_smoother)
- py2exe (for standalone)

Install the 3 last modules by using pip:

    python3 -m pip install BeautifulSoup4
    python3 -m pip install pygments
    python3 -m pip install py2exe

Run
===

block_generator
---------------

    python3 block_generator.py

simple_loot_fixer
-----------------

Change the Show/Hide header comment then run:

    python3 simple_loot_fixer 'Classy Item Filter'

Test
====

    python3 -m unittest discover -v

Standalone (Windows Only)
=========================

    python3 standalone.py simple_loot_fixer

To share with an another player:

    python3 standalone.py 1 simple_loot_fixer

This will generate a large executable file including your version of `python3x.dll`. You may chain several filenames in the command line (with or without the `.py` extension). More info:

    python3 standalone.py

State
=====

Good enough!
