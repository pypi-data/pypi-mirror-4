Introduction
============

zettwerk.fullcalendar integrates the jQuery FullCalendar into Plone 4.

Also check out zettwerk.ui for on-the-fly theming of the calendar and you plone site.

Use-Cases
=========

Basically this addon gives you a new view for Topics (and Folders) to display all event-like contenttypes with the jQuery Fullcalendar. Results from the Topic criteria which are not event-like CT´s will be ignored.

If you have developed you own event type it will be displayed as long as it implements the right interface or is based on ATEvent.

An Event will be 'all-day' if the starttime hour and minutes were left empty when the event was created.
All displayed events link to the corresponding object.

Time-Format
===========

Beginning with version 0.2.1 zettwerk.fullcalendar uses Plone site's preferred time format. It defaults to display a.m./p.m. which might not be so common in european contries. To change it, switch to the ZMI and click the portal_properties object. Then look for the site_properties and open it. Change the field 'localTimeOnlyFormat' to something more common like %H:%M.

Installation
============

Add zettwerk.fullcalendar to your buildout eggs. After running buildout and starting the instance, you can install Zettwerk Fullcalendar via portal_quickinstaller to your plone instance. zettwerk.fullcalendar requires Plone 4.

Usage
=====

Add a Topic anywhere on your site and set the criterias to your needs. All event-like results can now be displayed with the jQuery Fullcalendar by selecting the Calendar view in the Topic´s display menu. For Folders, just do the same: select the Calendar view and you are done. All event-like content objects will be shown.

Note
====

zettwerk.fullcalendar is out of the box ready to use zettwerk.ui to apply jquery.ui's css to the calendar view. There is only one problem with the ordering of the registered css in plone's portal_css (registry): if you installed zettwerk.ui after zettwerk.fullcalendar make sure to move the resource with id "++resource++jquery.fullcalendar/fullcalendar.css" to the bottom of all registered css files. You can do this by switching to the ZMI of you plone instance - click portal_css - search the id given above und use the arrows to move it down. At the end click "save".
