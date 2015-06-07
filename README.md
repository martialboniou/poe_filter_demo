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

- replace every Smartblock header's changes in [antnee](http://www.pathofexile.com/forum/view-thread/1245785) loot filter

Requirement
===========

- Install python 3.3+
- Install BeautifulSoup and Pygments 2.0


    python3 -m pip install BeautifulSoup4
    python3 -m pip install pygments

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

State
=====

Good enough!
