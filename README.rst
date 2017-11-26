Cryptocurrency
==============

| Version: 0.0.1
| Released: 2017-11-26
|

Install using::

    pip3 install --user --upgrade .

Introduction
------------

This program reads a file containing transactions to determine the total number 
of cryptocurrency tokens are held and reports on the current value of the 
portfolio.

The transactions are read from a file contained in ~/.config/cryptocurrency. The 
filename should be *transactions.gpg* or *transactions*.  The following in an 
example of a transactions file::

    from cryptocurrency import Account, BTC, ETH, BCH, ZEC

    zeus = Account('zeus')
    hermes = Account('hermes')
    persephone = Account('persephone')

    zeus.transaction(BTC(5, 120), '130905', 605, 'initial purchase - coinbase')
    zeus.transaction(BCH(5, 0), '170801', 0, 'fork of bitcoin')
    zeus.transaction(BTC(-2, 4100), '170917', 0, 'convert to ether')
    zeus.transaction(ETH(28.22784256, 297), '170917', 0, 'convert from bitcoin')
    zeus.transaction(BTC(-1, 4400), '170930', 0, 'Gift to Hermes')
    hermes.transaction(BTC(1, 4400), '170930', 0, 'Gift from Zeus')
    zeus.transaction(BTC(-1, 4400), '170930', 0, 'Gift to Persephone')
    persephone.transaction(BTC(1, 4400), '170930', 0, 'Gift from Zeus')
    zeus.transaction(BTC(5, 5240), '171012', 26205, 'purchase - GDAX')
    zeus.transaction(ETH(-1, 400), '171123', 0, 'Gift to Hermes')
    hermes.transaction(ETH(1, 400), '171123', 0, 'Gift from Zeus')
    zeus.transaction(ETH(-1, 400), '171123', 0, 'Gift to Persephone')
    persephone.transaction(ETH(1, 400), '171123', 0, 'Gift from Zeus')

The first argument of transaction is the token involved in the transaction. For 
example, 'ETH(2, 400)', which signifies that 2 ether tokens were acquired for 
a cost of $400 each. The second argument is the date, in the form YYMMDD. The 
third argument is the cost, in US dollars. This should equal tokens*price+fee.  
The final argument is a comment.

In this transactions file, three accounts are created, one each for Zeus, 
Hermes, and Persephone. Once defined, transactions are associated with the three 
accounts.

When running the cryptocurrency program, you can request information about each 
of the accounts individually or as a group.
