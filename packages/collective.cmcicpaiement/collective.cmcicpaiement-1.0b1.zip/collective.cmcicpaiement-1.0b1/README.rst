Introduction
============

This addon provide components to create the UI that will let you make a simple
paiement process to the `CM CIC paiement <https://www.cmcicpaiement.fr/>`_ 
solution

It can't be use alone, you must provide custom implementation for
your contents

How to install
==============

This addon can be installed has any other addons. please follow official
documentation_

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
.. image:: https://secure.travis-ci.org/toutpt/collective.categories.png
    :target: http://travis-ci.org/toutpt/collective.categories

You will find settings in the registry ( /portal_registry )

Components
==========

Aller form
----------

This addon add a base Browser to build an "Aller" form. The idea
is to adapt and implement the current context and request to be an order.

An order must provide following elements:

* montant: the amount of the order
* reference: the id of the order

You can achieve this in many way: Having a cart done with simplecartjs
with an Order content type that will provide thoses information. 
You will then just have to create the view inheriting from 
collective.cmcicpaiement.aller.AllerForm , implements montant and reference
method and call aller_form in your template to render the paid button that
will do the job.

Retour
------

This addon manage the "Retour" phase and response to the bank.
It use the zope event infrastructure to notify the system of paiements.

The retour URL must be configured by the bank and must be:

  yoursite.com/@@cmcic_retour

event example::

    <subscriber
      for="collective.cmcicpaiement.retour.IRetourEvent"
      handler=".retour.retour_handler" />
    
    
    def retour_handler(event):
    
        if event.code_retour == "Annulation":
            # Payment has been refused
            # The payment may be accepted later
            # put your code here (email sending / Database update)
            logger.info('paiement refused')
    
        elif event.code_retour == "payetest":
            # Payment has been accepeted on the test server
            # put your code here (email sending / Database update)
            logger.info('paiement accepted from test server')
    
        elif event.code_retour == "paiement":
            # Payment has been accepeted on the productive server
            # put your code here (email sending / Database update)
            logger.info('paiement accepted from production server')
    
        #*** ONLY FOR MULTIPART PAYMENT ***#
        elif event.code_retour == "paiement_pf2" or event.code_retour == "paiement_pf3" or event.code_retour == "paiement_pf4":
            # Payment has been accepted on the productive server for the part #N
            # return code is like paiement_pf[#N]
            # put your code here (email sending / Database update)
            # You have the amount of the payment part in event.montantech
            logger.info('paiement accepted from production server for a part')
    
        elif event.code_retour == "Annulation_pf2" or event.code_retour == "Annulation_pf3" or event.code_retour == "Annulation_pf4":
            # Payment has been refused on the productive server for the part #N
            # return code is like Annulation_pf[#N]
            # put your code here (email sending / Database update)
            # You have the amount of the payment part in event.montantech
            logger.info('paiement refused from production server for a part')


Credits
=======

|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina-Corpus <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
