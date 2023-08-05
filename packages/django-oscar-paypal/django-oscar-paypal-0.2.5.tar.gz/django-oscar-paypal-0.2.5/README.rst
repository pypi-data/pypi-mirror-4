===============================
PayPal package for django-oscar
===============================

.. image:: https://secure.travis-ci.org/tangentlabs/django-oscar-paypal.png

This package provides integration between django-oscar_ and both `PayPal
Express`_ and `PayPal Payflow Pro`_.

.. _django-oscar: https://github.com/tangentlabs/django-oscar
.. _`PayPal Express`: https://www.paypal.com/uk/cgi-bin/webscr?cmd=_additional-payment-ref-impl1
.. _`PayPal Payflow Pro`: https://merchant.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=merchant/payment_gateway

These payment options can be used individually or both together.  Further, the
package is structured so that it can be used without Oscar if you so wish.

* `Full documentation`_
* `Continuous integration status`_

.. _`Full documentation`: http://django-oscar-paypal.readthedocs.org/en/latest/
.. _`Continuous integration status`: http://travis-ci.org/#!/tangentlabs/django-oscar-paypal

Having problems or got a question?

* Have a look at the sandbox installation as this is a sample Oscar project
  integrated with both PayPal options.  See the contributing guide within the
  docs for instructions on how to set up the sandbox locally.
* Ping `@django_oscar`_ with quick queries.
* Ask more detailed questions on the Oscar mailing list: django-oscar@googlegroups.com.
* Use Github for submitting issues and pull requests.

.. _`@django_oscar`: https://twitter.com/django_oscar

The package is released under the new BSD license.

Changelog
---------

0.2.5
~~~~~
* Fix silly bug with reference transactions

0.2.4
~~~~~
* Fix bug with installing templates

0.2.3
~~~~~
* Fix bug with amount formats not being validated properly
* Adjust txn model to allow virtually everything to be nullable

0.2.2
~~~~~
* Add support for specifying transaction currency

0.2.1
~~~~~
* Fix packaging issues
* Remove dead templates
* With API docs

0.2
~~~
Includes support for Payflow Pro.

0.1
~~~
Includes support for Express Checkout.
