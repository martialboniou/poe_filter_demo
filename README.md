Note
====

This is a demo created for documentation purpose. The author only spent 3 hours.

Goal
====

- Extract `item-data` from the website of [Path Of Exile](http://www.pathofexile.com) game by Grinding Gear Games
- Generate Awakening compatible loot filter blocks from:

  - crossed requirements (mainly for armour; ie. STR/DEX, INT...)
  - attributs (ie. base weapon w/ Attacks per second > 1.5; **TODO**)

- Compress item names in list (**TODO**)

Usage
=====

- Install python 3.3+ (Pygments 2.0 will be required later as a lexer)
- Install BeautifulSoup from python:

    python3 -m pip install BeautifulSoup4
