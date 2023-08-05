Introduction
============

collective.MockMailHost enables integration testing of email functionality from Plone.
Simply add this egg to your [test] runner section, and install this product from PloneTestCase.

DO NOT USE THIS PRODUCT on your running Plone site. It replaces the standard MailHost with a Mock
MailHost that you can poke at to check email content and recipients.

Has been tested with Plone 4 but should also work with earlier versions.

