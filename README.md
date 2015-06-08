Note
====

This is a demo created for documentation purpose.

Goal
====

classy_generator
----------------

- Extract `item-data` from the website of [Path Of Exile](http://www.pathofexile.com) game by Grinding Gear Games
- Generate Awakening compatible loot filter Show blocks for crossed requirements (ie. STR/DEX, INT... in `item-data/armour`)
- Compress item names in list by checking there's no name conflict with other databases (weapons, currency, jewelry...)

classy_smoother
---------------

- replace every Smartblock header's changes in [antnee](http://www.pathofexile.com/forum/view-thread/1245785) loot filter or any other filters using a Smartblocks convention

Requirement
===========

- python 3.3+ (tested on 3.4.3)
- BeautifulSoup (for classy_generator)
- Pygments 2.0 (for classy_smoother)
- py2exe (for standalone)

By using pip:

    python3 -m pip install BeautifulSoup4
    python3 -m pip install pygments
    python3 -m pip install py2exe

Run
===

classy_generator
----------------

    python3 classy_generator.py

classy_smoother
---------------

Change the Show/Hide header:

    python3 classy_smoother 'Classy Item Filter'

Test
====

    python3 -m unittest discover -v

Standalone (Windows Only)
=========================

    python3 standalone.py classy_smoother

To share with an another player:

    python3 standalone.py 1 classy_smoother

This will generate a large executable file including your version of `python3x.dll`. You may chain several filenames in the command line (with or without the `.py` extension). More info:

    python3 standalone.py

State
=====

Good enough!
