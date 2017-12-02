Cryptocurrency
==============

| Version: 0.0.7
| Released: 2017-12-01
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
    hermes = Account('hermes', False)
    persephone = Account('persephone', False)

    zeus.transaction(      BTC(5, 120),  '130905', 'initial purchase (coinbase)')
    zeus.transaction(      BCH(5),       '170801', 'fork of bitcoin')
    zeus.transaction(      BTC(-2),      '170917', 'convert to ether')
    zeus.transaction(      ETH(28.2276), '170917', 'convert from bitcoin')
    zeus.transaction(      BTC(-1),      '170930', 'Gift to Hermes')
    hermes.transaction(    BTC(1),       '170930', 'Gift from Zeus')
    zeus.transaction(      BTC(-1),      '170930', 'Gift to Persephone')
    persephone.transaction(BTC(1),       '170930', 'Gift from Zeus')
    zeus.transaction(      BTC(5, 5240), '171012', 'purchase (GDAX)')
    zeus.transaction(      ETH(-1),      '171123', 'Gift to Hermes')
    hermes.transaction(    ETH(1),       '171123', 'Gift from Zeus')
    zeus.transaction(      ETH(-1),      '171123', 'Gift to Persephone')
    persephone.transaction(ETH(1),       '171123', 'Gift from Zeus')
    zeus.transaction(      BCH(0.0005),  '170801', 'transaction fee')

Use *Account* to create an account that can hold a sequence of transactions.  
*Account* take an optional boolean second argument. It indicates whether the 
account should be included in the collection accounts that are displayed by 
default.

The first argument of transaction is the token involved in the transaction. For 
example, 'ETH(2, 400)', which signifies that 2 ether tokens were acquired for 
a cost of $400 each. Leave the cost out if it is a transfer rather than 
a purchase or sale. The second argument is the date, in the form YYMMDD.  The 
final argument is a comment.

In this transactions file, three accounts are created, one each for Zeus, 
Hermes, and Persephone. Once defined, transactions are associated with the three 
accounts.

When running the cryptocurrency program, you can request information about each 
of the accounts individually or as a group. For example:

    cryptocurrency       -- show summary of default accounts without transactions
    cryptocurrency -t    -- show summary of default accounts with transactions
    cryptocurrency zeus  -- show summary of zeus account without transactions
    cryptocurrency hermes persephone
                         -- show summary of hermes and persephone accounts
    cryptocurrency -t hermes persephone
                         -- same with transactions

    cryptocurrency -p    -- show current prices rather than holdings
