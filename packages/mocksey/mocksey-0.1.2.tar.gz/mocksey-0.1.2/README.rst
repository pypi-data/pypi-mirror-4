mocksey
=======

Stupidly-simple python mocking utility with moxie.

|BuildImage|_

Mocksey Motivation
==================

I was teaching a class on unit testing to a group of co-workers who were familiar with `Simple Test for PHP <http://www.simpletest.org/>`_ so I hacked together what is becoming Mocksey.

Mocksey the TDD'd version of that TDD utilty. `It's so meta even this acronym <http://xkcd.com/917/>`_.

Basic Usage
===========

It's pretty simple.  Create a mocked object with generate_mock, inject it (or monkey patch) and set up your assertions.  After your function call(s), simply call 'run_asserts' and win!

The unit tests are a pretty decent working example.


License
=======
This software is hereby released under the MIT License, as seen in the LICENSE file

.. |BuildImage| image:: https://secure.travis-ci.org/mitgr81/mocksey.png
.. _BuildImage: https://travis-ci.org/mitgr81/mocksey