.. contents::

Introduction
============

Enough is enough. Microsoft Internet Explorer 8 was released in early 2009.
For its time, it was a decent browser, but today it is still in use by a
significant portion of the web population, and its time is now up.

As any web developer will tell you, working with outdated browsers is one of
the most difficult and frustrating things they have to deal with on a daily
basis, taking up a disproportionate amount of their time. Beyond that, IE 8's
support for modern web standards is lacking, restricting what developers can
create and holding the web back.

Usage
------

This is a Plone viewlet that shows your site visitors a banner prompting them
to upgrade their browser for a better experience.

Add ``collective.ie8nomore`` to your list of python eggs. For example, for 
buildout::

  [buildout]
  
  eggs = 
      ...
      collective.ie8nomore
      
You don't need to install the product in the control panel. You just need to
restart Plone and configure the order of your viewlets. To be able to do so, 
visit http://plonesite/@@manage-viewlets .
