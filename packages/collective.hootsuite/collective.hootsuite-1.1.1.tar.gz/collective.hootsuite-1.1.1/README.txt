.. contents::

Introduction
============

Plone module to subscribe content creation to a hootsuite account in order to publish a notification
on hootsuite social networks every time a content is published schedulled with the publication date.

Installation
============

Just add the egg to the buildout configuration.

Configuration
=============

At the hootsuite configuration panel (on plone control panel):

 * You need a Hootsuite client_id and secret_key that needs to aproved by hootsuite app directory
 
 * After saving the Hootsuite keys you should press connect link on the configuration panel to get 
   the authorization code (alert it expires so you need to connect again after one year)

 * When you have the token field you should press the refresh button in order to get the available
   services. After loading them you can choose at what services you want to push the notification.

 * Finally you need to choose which content types you want to use

 When you have configured the content types and social networks the system will push a notification
 every time one content of this type is published (depends on workflow published). If the content has
 a effective date (publication date) it will schedule the notification to that moment.

Credits
=======

Developed by Iskra Desenvolupament SCCL (http://iskra.cat)

Sponsored by Ajuntament de Sant Adrià de Besos

