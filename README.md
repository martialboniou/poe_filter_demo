Note
====

This is a demo created for documentation purpose.

Goal
====

- Extract `item-data` from the website of [Path Of Exile](http://www.pathofexile.com) game by Grinding Gear Games
- Generate Awakening compatible loot filter Show blocks for crossed requirements (ie. STR/DEX, INT... in `item-data/armour`)
- Compress item names in list by checking there's no name conflict with other databases (weapons, currency, jewelry... *TODO* add map placeholders and maraketh weapons

Usage
=====

- Install python 3.3+ (Pygments 2.0 will be required later as a lexer)
- Install BeautifulSoup from python:

    python3 -m pip install BeautifulSoup4
    python3 classy_generator.py

Current State
=============

Good enough!
