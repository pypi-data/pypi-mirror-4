django-fakeimg
==============

A django port of fakeimg.pl

Installation
============

Run `pip install django-fakeimg`.

Add `fakeimg` to your `INSTALLED_APPS` setting:

	INSTALLED_APPS = (
	    ...
	    'fakeimg',
	)

Example usage
=============

In a template,

	<img src="{% url fakeimg_placeholder 100 %}" />
	<img src="{% url fakeimg_placeholder 100 200 %}" />
	<img src="{% url fakeimg_placeholder 100 200 'ccc' 'ddd'%}" />
	<img src="{% url fakeimg_placeholder 100 %}?text=Hello&fond=lobster" />