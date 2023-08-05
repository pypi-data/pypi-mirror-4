Introduction
============

This is a Plone-4 add-on that aims to help especially smaller sites to get started quicker and easier.

The goal is to give the possibility to configure most common website-usecases via the webinterface for mortals. No programming needed.

Most functionalities are pulled in by small splitted plone-add-ons, named below, so you can roll your own combinations, installing them individually, in case you don't need parts of the whole package.

- Sets the navigation to only show folders.

- Removes the default top- and footer-viewlets and inserts sample static-text-portlets instead, for easy editing the top- and footer-part through the web via adi.simplestructure and Products.ContentWellPortlets

- Adds a top-main-dropdownmenu via adi.dropdownmenu, collective.sitemap and Products.ContentWellPortlets

- Removes Plone's public.css styles for border, colors, backgrounds and other little tweaks, to give an easier starting-point for your own styling via adi.resetcss.

- Removes Plone's default contents (news, users, events, front-page) and portlets and replaces them with some sample content (about, contact, etc.) via adi.init and adi.content

