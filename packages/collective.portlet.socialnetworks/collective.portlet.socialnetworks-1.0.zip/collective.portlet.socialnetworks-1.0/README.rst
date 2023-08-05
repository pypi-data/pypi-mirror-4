Introduction
============

This addon provide a portlet to let people follow your company accros
multiple social networks

How it works / to use
=====================

You can add social networks (to follow) using the settings registry
''.

To configure in your own policy do as follow::

   <record name="collective.portlet.socialnetworks">
       <value>
         <element>facebook|https://www.facebook.com/cirbcibg</element>
         <element>twitter|https://twitter.com/cirb_cibg</element>
         <element>linkedin|http://www.linkedin.com/company/cirb_cibg</element>
         <element>youtube|http://www.youtube.com/user/CIRBCIBG</element>
       </value>
   </record>

This addon build links with icons and so provide icons. Provided icons are for
the following social networks:

* blogger
* digg
* facebook
* flickr
* google plus
* linkedin
* myspace
* pinterest
* stumbleupon
* tumblr
* twitter
* vimeo
* youtube

How to customize icons
======================

To change used icons you have two solution:
* create a browser resource directory with the name of this addon and provide
the new set of icons you want to use.
* override the template using z3c.jbot (or plone.app.themingplugins) to change
icons urls.

Credits
=======

Icons
-----

|3d-designbolts|_

|makinacom|_


* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

|cirb|_ CIRB / CIBG

* `Contact CIRB <mailto:irisline@irisnet.be>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |cirb| image:: http://www.cirb.irisnet.be/logo.jpg
.. _cirb: http://cirb.irisnet.be
.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
.. |3d-designbolts| image:: http://icons.iconarchive.com/icons/designbolts/3d-social/icons-390.jpg
.. _3d-designbolts: http://www.iconarchive.com/show/3d-social-icons-by-designbolts.html

