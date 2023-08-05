==================
niteoweb.ipn.jvzoo
==================

A Plone add-on that integrates JVZoo digital products retailer system with
Plone to enable paid memberships on your site.

* `Source code @ GitHub <https://github.com/niteoweb/niteoweb.ipn.jvzoo>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/niteoweb.ipn.jvzoo>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/niteoweb/niteoweb.ipn.jvzoo>`_


How it works
============

#. Visitor comes to your site and clicks an Order link.

#. Visitor is sent to JVZoo's order form (on http://jvzoo.com), where she
   enters her personal information and performs payment.

#. If payment was successful, JVZoo sends a POST request to a special view on
   your Plone site (``/@@jvzoo``).

#. The ``@@jvzoo`` view parses this POST data from JVZoo and verifies it
   against the `Secret Key` you've set in the `Plone control panel`.

#. If all checks out, ``@@jvzoo`` calls an appropriate action provided by the
   ``niteoweb.ipn.core`` package (on which this package depends on).


Transaction type to ``niteoweb.ipn.core`` action mapping
========================================================

JVZoo supports different `Transaction types`, like `Sale`, `Cancellation`,
`Refund`, etc. These are mapped to actions provided by ``niteoweb.ipn.core``.

Mapping:
 * SALE -> enable_member
 * BILL -> enable_member
 * RFND -> disable_member
 * CGBK -> disable_member
 * INSF -> disable_member
 * CANCEL-REBILL -> disable_member
 * UNCANCEL-REBILL -> enable_member

Transaction types are explained in the JVZoo IPN documentation available on
http://support.jvzoo.com/Knowledgebase/Article/View/17/0/jvzipn.

Installation
============

To install `niteoweb.ipn.jvzoo` you simply add ``niteoweb.ipn.jvzoo``
to the list of eggs in your buildout, run buildout and restart Plone.
Then, install `niteoweb.ipn.jvzoo` using the Add-ons control panel.

Configuration
=============

JVZoo
-----

Go to `JVZoo.com <http://jvzoo.com>`_ and use ``Sellers`` ->
``Add a Product`` to add a new `Product`.

Then check the option ``External Program Integration``. For `URL`
set ``http://yoursite.com/@@jvzoo``. Under the ``My Account`` page
set the ``JVZIPN Secret Key``.


Plone
-----

Go to ``Site Setup`` -> ``Configuration Registry`` control panel form and
configure the ``Secret Key`` field by pasting it in the `niteoweb ipn jvzoo
interfaces IJVZooSettings secretkey` field.


Test it
=======

You are now ready to do a test buy! Go back to ``Sellers`` and click
``Test Purchases``. Select a product, click ``Create Test Purchase Code`` and
finish by clicking the link in ``Buy / Link`` column in the table below. In
order for the purchase link to work, the product needs to be activated in
``Sellers Dashboard`` (select a product and check ``Allow Sales``).

Before you finish the transaction, you of course need to set up your Plone
site to receive JVZoo server notifications.

Confirm by logging-in to http://jvzoo.com and checking to see if there were any
purchases (on ``Sellers`` tab). Also check if your received an email with
username and password for accessing your site and try to login with them.


Tips & Tricks
=============

JVZoo IPN API documentation
---------------------------

Available at http://support.jvzoo.com/Knowledgebase/Article/View/17/0/jvzipn.


Mocked request
--------------

If you want to mock a request from JVZoo in your local development environment,
run a command like this::

    $ curl -d "ccustname=JohnSmith&ccuststate=&ccustcc=&ccustemail=test@email.com&cproditem=1&cprodtitle=TestProduct&cprodtype=STANDARD&ctransaction=SALE&ctransaffiliate=affiliate@email.com&ctransamount=1000&ctranspaymentmethod=&ctransvendor=&ctransreceipt=1&cupsellreceipt=&caffitid=&cvendthru=&cverify=AACDD10E&ctranstime=1350388651" http://localhost:8080/Plone/@@jvzoo

The command above assumes you have set your `Secret Key` in Plone to
``secret`` and you have created a group with ``ipn_1`` id.

