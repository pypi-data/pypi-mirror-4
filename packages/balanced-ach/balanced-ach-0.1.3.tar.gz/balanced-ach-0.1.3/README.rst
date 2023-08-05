Balanced ACH
------------

Python library for `Balanced ACH <https://github.com/balanced/balanced-api/blob/ach/README.md>`_ payments. 

.. image:: https://secure.travis-ci.org/balanced/balanced-ach-python.png?branch=master
   :target: http://travis-ci.org/balanced/balanced-ach-python

To Install
==========

Simply::

   pip install balanced-ach
   
or if you prefer::

    easy_install balanced-ach
    
Requirements
============

- `Python <http://python.org/>`_ >= 2.6, < 3.0
- `wac <https://github.com/bninja/wac/>`_ >=0.11
- `iso8601 <http://code.google.com/p/pyiso8601/>`_ >=0.1.4,
- `simplejson <https://github.com/simplejson/simplejson>`_ >=2.3.2

Usage
=====

.. code:: python

    import balanced_ach

    print "create a bank account"
    bank_account = balanced_ach.BankAccount(
        name='Gottfried Leibniz',
        account_number='3819372930',
        routing_number='121042882',
        type='checking',
    ).save()
    
    print "Cool, let's credit that bank account for $1.01 USD"
    credit = bank_account.credit(101)
    
    print "Cool, let's debit that bank account for $4.55 USD"
    debit = bank_account.debit(455)
    
    print "Want to credit that bank account $1.01 USD without creating it? Cool"
    credit = balanced_ach.Credit(
        amount=101,
        bank_account=dict(
            name='Gottfried Leibniz',
            account_number='3819372930',
            routing_number='121042882',
            type='checking',
    )).save()
    
    print "Want to debit that bank account $4.55 USD without creating it? Cool"
    debit = balanced_ach.Debit(
        amount=101,
        bank_account=dict(
            name='Gottfried Leibniz',
            account_number='3819372930',
            routing_number='121042882',
            type='checking',
    )).save()
    
    print "and there you have it 8-)"
        

Issues
======
Please use appropriately tagged github `issues <https://github.com/balanced/balanced-ach-python/issues>`_ to request features or report bugs.


Contributing
============

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Write your code **and tests**
4. Ensure all tests still pass (`nosetests -svx tests`)
5. Commit your changes (`git commit -am 'Add some feature'`)
6. Push to the branch (`git push origin my-new-feature`)
7. Create new pull request
