=====================
ztfy.jqueryui package
=====================

.. contents::

What is ztfy.jqueryui ?
=======================

ztfy.jqueryui is a set of javascript resources (and their dependencies) allowing any application to easily
use a set of JQuery plug-ins; when possible, all CSS and JavaScript resources are already minified
via Yahoo 'yui-compressor' tool.

Most of these plug-ins are used by default ZTFY skins and packages.

Currently available plug-ins include :
 - the JQuery engine
 - jquery-alerts
 - jquery-colorpicker
 - jquery-datatables
 - jquery-datetime
 - jquery-fancybox
 - jquery-form
 - jqeury-imgareaselect
 - jqeury-jscrollpane
 - jquery-jsonrpc
 - jquery-jtip
 - jquery-multiselect
 - jquery-progressbar
 - jquery-tools
 - jquery-treetable
 - jquery-ui


How to use ztfy.jqueryui ?
==========================

All JQuery resources are just defined as Fanstatic libraries. ZCML registration is not required.

Using a given plug-in is as simple as using the following syntax in any HTML view: ::

    >>> from ztfy.jqueryui.browser import jquery
    >>> jquery.need()

Given that, all plug-in dependencies will automatically be included into resulting HTML page.

A single resource can be required several times for a single page, but the resulting resources will
be included only one via the Fanstatic machinery.

When available, a minified version as well as a "clear source" version are defined. When using
ZTFY.webapp package, the first one is used in "deployment" mode while the second one is automatically
used in "development" mode to make debugging very easy.


Requiring plugins through templates
===================================

If, for example, you want to call resources from a site's layout for which you don't have any Python
class, you can call it directly from a page template, like this: ::

    <tal:var replace="fanstatic:ztfy.jqueryui#jquery" />

The "fanstatic:" expression is provided by ztfy.utils package.
