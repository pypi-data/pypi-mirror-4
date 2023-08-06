### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
from fanstatic import Library, Resource, Group

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


library = Library('ztfy.jqueryui', 'resources')

# Main JQuery library
jquery_13 = Resource(library, 'js/jquery-1.3.js', minified='js/jquery-1.3.min.js', bottom=True)
jquery_14 = Resource(library, 'js/jquery-1.4.4.js', minified='js/jquery-1.4.4.min.js', bottom=True)
jquery_17 = Resource(library, 'js/jquery-1.7.2.js', minified='js/jquery-1.7.2.min.js', bottom=True)
jquery_19 = Resource(library, 'js/jquery-1.9.1.js', minified='js/jquery-1.9.1.min.js', bottom=True)
jquery = jquery_17

jquery_migrate = Resource(library, 'js/jquery-migrate-1.1.1.js', minified='js/jquery-migrate-1.1.1.min.js',
                          depends=[jquery_19], bottom=True)

# JQuery UI
jquery_ui_css_main = Resource(library, 'css/jquery-ui-1.7.3.css',
                              minified='css/jquery-ui-1.7.3.min.css')
jquery_ui_css = Resource(library, 'css/jquery-ui.theme.css',
                         minified='css/jquery-ui.theme.min.css',
                         depends=[jquery_ui_css_main])

jquery_ui_core_17 = Resource(library, 'js/jquery-ui-core-1.7.3.min.js',
                             depends=[jquery, jquery_ui_css],
                             bottom=True)
jquery_ui_base_17 = Resource(library, 'js/jquery-ui-base-1.7.3.min.js',
                             depends=[jquery_ui_core_17, jquery_ui_css],
                             bottom=True)
jquery_ui_widgets_17 = Resource(library, 'js/jquery-ui-widgets-1.7.3.min.js',
                                depends=[jquery_ui_base_17, jquery_ui_css],
                                bottom=True)
jquery_ui_effects_17 = Resource(library, 'js/jquery-ui-effects-1.7.3.min.js',
                                depends=[jquery_ui_base_17, jquery_ui_css],
                                bottom=True)
jquery_ui_all_17 = Group(depends=[jquery_ui_widgets_17, jquery_ui_effects_17])

jquery_ui_core = Resource(library, 'js/jquery-ui-core-1.8.16.min.js',
                          depends=[jquery, jquery_ui_css],
                          bottom=True)
jquery_ui_base = Resource(library, 'js/jquery-ui-base-1.8.16.min.js',
                          depends=[jquery_ui_core, jquery_ui_css],
                          bottom=True)
jquery_ui_widgets = Resource(library, 'js/jquery-ui-widgets-1.8.16.min.js',
                             depends=[jquery_ui_base, jquery_ui_css],
                             bottom=True)
jquery_ui_effects = Resource(library, 'js/jquery-ui-effects-1.8.16.min.js',
                             depends=[jquery_ui_base, jquery_ui_css],
                             bottom=True)
jquery_ui_all = Group(depends=[jquery_ui_widgets, jquery_ui_effects])

# JQuery Tools
jquery_tools_11 = Resource(library, 'js/jquery-tools-1.1.2.min.js',
                           depends=[jquery],
                           bottom=True)

jquery_tools_12 = Resource(library, 'js/jquery-tools-1.2.7.js',
                           minified='js/jquery-tools-1.2.7.min.js',
                           depends=[jquery],
                           bottom=True)
jquery_tools = jquery_tools_12

# JQuery I18n
jquery_i18n = Resource(library, 'js/jquery-i18n.js',
                       minified='js/jquery-i18n.min.js',
                       depends=[jquery],
                       bottom=True)

# JQuery Form
jquery_form = Resource(library, 'js/jquery-form-3.27.js',
                       minified='js/jquery-form.min.js',
                       depends=[jquery],
                       bottom=True)

# JQuery Tipsy
jquery_tipsy_css = Resource(library, 'css/jquery-tipsy.css')
jquery_tipsy = Resource(library, 'js/jquery-tipsy.js',
                        depends=[jquery, jquery_tipsy_css],
                        bottom=True)

# JQuery Cookie
jquery_cookie = Resource(library, 'js/jquery-cookie.js',
                         minified='js/jquery-cookie.min.js',
                         depends=[jquery],
                         bottom=True)

# JQuery mousewheel
jquery_mousewheel = Resource(library, 'js/jquery-mousewheel.js',
                             minified='js/jquery-mousewheel.min.js',
                             depends=[jquery],
                             bottom=True)

# JQuery layout
jquery_layout_css = Resource(library, 'css/jquery-layout.css',
                             minified='css/jquery-layout.min.css')
jquery_layout = Resource(library, 'js/jquery-layout.js',
                         minified='js/jquery-layout.min.js',
                         depends=[jquery_ui_effects, jquery_layout_css],
                         bottom=True)

# JQuery JSON-RPC
jquery_json2 = Resource(library, 'js/json2.js',
                        minified='js/json2.min.js',
                        bottom=True)
jquery_jsonrpc = Resource(library, 'js/jquery-jsonrpc.js',
                          minified='js/jquery-jsonrpc.min.js',
                          depends=[jquery, jquery_json2], bottom=True)

# JQuery Alerts
jquery_alerts_css = Resource(library, 'css/jquery-alerts.css',
                             minified='css/jquery-alerts.min.css')
jquery_alerts = Resource(library, 'js/jquery-alerts.js',
                         minified='js/jquery-alerts.min.js',
                         depends=[jquery, jquery_i18n, jquery_alerts_css],
                         bottom=True)

# JQuery FancyBox
jquery_fancybox_css = Resource(library, 'css/jquery-fancybox-1.3.1.css',
                               minified='css/jquery-fancybox.min.css')
jquery_fancybox = Resource(library, 'js/jquery-fancybox-1.3.1.js',
                           minified='js/jquery-fancybox.min.js',
                           depends=[jquery, jquery_fancybox_css],
                           bottom=True)

# JQuery TreeTable
jquery_treetable_css = Resource(library, 'css/jquery-treeTable.css',
                                minified='css/jquery-treeTable.min.css')
jquery_treetable = Resource(library, 'js/jquery-treeTable.js',
                            minified='js/jquery-treeTable.min.js',
                            depends=[jquery, jquery_treetable_css],
                            bottom=True)

# JQuery DataTables
jquery_datatables_css = Resource(library, 'css/jquery-datatables.css',
                                 minified='css/jquery-datatables.min.css')
jquery_datatables = Resource(library, 'js/jquery-datatables.js',
                             minified='js/jquery-datatables.min.js',
                             depends=[jquery, jquery_datatables_css],
                             bottom=True)

# JQuery DateTime
jquery_datetime_css = Resource(library, 'css/jquery-datetime.css',
                               minified='css/jquery-datetime.min.css')
jquery_datetime = Resource(library, 'js/jquery-datetime.js',
                           minified='js/jquery-datetime.min.js',
                           depends=[jquery, jquery_datetime_css],
                           bottom=True)

# JQuery ColorPicker
jquery_colorpicker_css = Resource(library, 'css/jquery-colorpicker.css',
                                  minified='css/jquery-colorpicker.min.css')
jquery_colorpicker = Resource(library, 'js/jquery-colorpicker.js',
                              minified='js/jquery-colorpicker.min.js',
                              depends=[jquery, jquery_colorpicker_css],
                              bottom=True)

# JQuery imgAreaSelect
jquery_imgareaselect_css = Resource(library, 'css/jquery-imgareaselect.css',
                                    minified='css/jquery-imgareaselect.min.css')
jquery_imgareaselect = Resource(library, 'js/jquery-imgareaselect.js',
                                minified='js/jquery-imgareaselect.min.js',
                                depends=[jquery, jquery_imgareaselect_css],
                                bottom=True)

# JQuery jScrollPane
jquery_jscrollpane_css = Resource(library, 'css/jquery-jscrollpane.css',
                                  minified='css/jquery-jscrollpane.min.css')
jquery_jscrollpane = Resource(library, 'js/jquery-jscrollpane.js',
                              minified='js/jquery-jscrollpane.min.js',
                              depends=[jquery, jquery_mousewheel, jquery_jscrollpane_css],
                              bottom=True)

# JQuery MultiSelect
jquery_multiselect_css = Resource(library, 'css/jquery-multiselect.css',
                                  minified='css/jquery-multiselect.min.css')
jquery_multiselect = Resource(library, 'js/jquery-multiselect.js',
                              minified='js/jquery-multiselect.min.js',
                              depends=[jquery, jquery_multiselect_css],
                              bottom=True)

# JQuery dotdotdot
jquery_dotdotdot = Resource(library, 'js/jquery-dotdotdot.js',
                            depends=[jquery],
                            bottom=True)

# JQuery LiquidCarousel
jquery_liquidcarousel_css = Resource(library, 'css/jquery-liquidcarousel.css')
jquery_liquidcarousel = Resource(library, 'js/jquery-liquidcarousel.js',
                                 depends=[jquery],
                                 bottom=True)

# JQuery UploadProgress
jquery_progressbar = Resource(library, 'js/jquery-progressbar.js',
                              minified='js/jquery-progressbar.min.js',
                              depends=[jquery],
                              bottom=True)

# JQuery TinyMCE
jquery_tinymce = Resource(library, 'js/tiny_mce/tiny_mce.js',
                          depends=[jquery],
                          bottom=True)
