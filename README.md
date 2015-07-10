Note
====

This is a demo created for documentation purpose.

Goal
====

LootWizard
----------

- Graphic Smartblock switcher (including tree view); see the [Antnee's Classy Item Filter](https://www.pathofexile.com/forum/view-thread/1245785)
- [Filtration](https://github.com/ben-wallis/Filtration) displays all blockgroups as they appeared in the loot filter, LootWizard only shows the blockgroups listed in the header comment (in the order chosen by loot filter creator)
- *Coming soon*: Display unreferenced blockgroups (smartblocks not written in the header comment may be changed then)

block_generator
----------------

- Extract `item-data` from the website of [Path Of Exile](http://www.pathofexile.com) game by Grinding Gear Games
- Generate Awakening compatible loot filter Show blocks for crossed requirements (ie. STR/DEX, INT... in `item-data/armour`)
- Compress item names in list by checking there's no name conflict with other databases (weapons, currency, jewelry...)

simple_loot_wizard
------------------

- Replace every Smartblock header's changes in [Antnee's Classy Item Filter](http://www.pathofexile.com/forum/view-thread/1245785) or any other filters using the [Muldini](https://www.reddit.com/r/pathofexile/comments/352vy0/loot_filter_one_filter_to_rule_them_all)'s convention

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

LootWizard
----------

    python3 LootWizard.py

block_generator
---------------

    python3 block_generator.py

simple_loot_wizard
------------------

Change the Show/Hide header comment then run:

    python3 simple_loot_wizard 'Classy Item Filter'

Test
====

    python3 -m unittest discover -v

Standalone (Windows Only)
=========================

    python3 standalone.py simple_loot_wizard

To share with an another player:

    python3 standalone.py 1 simple_loot_wizard

This will generate a large executable file including your version of `python3x.dll`. You may chain several filenames in the command line (with or without the `.py` extension). More info:

    python3 standalone.py

State
=====

Good enough!
