==================
 Mezzanine Careers
==================

Mezzanine Careers is a simple Job Posting application built for the `Django`_ based CMS `Mezzanine`_.

This app is NOT ready for production use but play as you will. It's pretty basic.

Features
========

* Create a list of job posting with delayed and expiring durations
* Provide basic templates to get started
* Seamlessly integrate with the Mezzanine CMS

Installation and Usage
======================

Install the app by using `pip`_::

  $ pip install mezzanine-careers

Add ``careers`` to ``INSTALLED_APPS`` and synchronize/migrate the database.

Go to the admin site and create new job posts in the ``Careers`` section

Development
===========

New features and fixes are welcome. Better if it comes with a patch or pull request. 
You can find the latest development sources at `GitHub`_.
Issues are tracked at the GitHub project page.

To-Do
=====

* add user posting form modelled or integrate mezzanine forms
* add user uploads (resumes, CVs, portfolio, etc.)
* add user email replies

.. _`Mezzanine`: http://mezzanine.jupo.org/
.. _`Django`: http://djangoproject.com/
.. _`pip`: http://www.pip-installer.org/
.. _`GitHub`: https://github.com/mogga/mezzanine-careers
