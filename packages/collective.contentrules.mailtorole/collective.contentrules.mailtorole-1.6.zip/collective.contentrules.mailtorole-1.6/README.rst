Introduction
============

Using content rules (available since Plone 3) it's very easy to register for
certain events and perform actions upon occurrence. One of these actions
provided by Plone is a mail action. 

A limitation in the supplied mail action is that one can only provide fixed
email addresses. But sometimes you'd like to send an email to a user having a
certain role on the object that was involved in triggering the content rule.

An examplary use case and reason for creation of this package is the reviewer 
role. If an object in a certain location of the site is submitted for
publication, you would like to inform the user that has the 'reviewer' role
on this area of the site that a new document/object is available for review.

Before contentrules was available in Plone the place to add this functionality
was to to create a python script and attach it to the workflow 'submit' 
transition that was used for the objects.

.. Note::
   This product supercedes collective.contentrules.mailtolocalrole_. 
   Extending that product's functionality with sending mail to global roles
   made it logical to rename the package. 

Installation
============

Add collective.contentrules.mailtorole to your buildout as an egg or
from source. No (generic setup) installation is necessary.

Usage
=====

Go to the Plone Control Panel, select Content Rules and add a new Rule. 
Under 'actions' you now have a new option: Send email to users with role.

The checkboxes "Acquire roles" and "Global roles" are worth noting:

- If both are unchecked, mail will only be sent to members having a local role 
  on the object.

- Checking "Acquire roles" will also send mail to users that have acquired the
  specified role from a parent of the object, ie. from higher up in the site.

- Checking "Global roles" will also send mail to users that have the specified
  role globally, that is in the entire site.

Credits
=======

Most of this package has been directly copied from the plone.app.contentrules
mail action. Additions have been made to check for directly assigned local
roles, acquired roles, global roles, fetching the e-mail To addresses from the
user objects, modification of the control panel action, translations and tests.
 
.. _collective.contentrules.mailtolocalrole: http://plone.org/products/collective-contentrules-mailtolocalrole/
