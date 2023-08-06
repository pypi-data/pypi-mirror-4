# -*- coding: utf-8 -*-

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource
from js.jqueryui import ui_button
from js.jqueryui import ui_droppable
from js.jqueryui import ui_widget


library = Library('jquery-ui-multiselect2', 'resources')

multiselect2_common_css = Resource(
    library,
    'css/common.css'
    )

multiselect2_css = Resource(
    library,
    'css/jquery-multiselect-2.0.css',
    )

multiselect2_js = Resource(
    library,
    'js/jquery-multiselect-2.0.js',
    depends=[ui_button, ui_droppable, ui_widget]
    )

multiselect2 = Group([multiselect2_css, multiselect2_js])

multiselect2_en = Resource(
    library,
    'js/locales/jquery-multiselect-2_en.js',
    depends=[multiselect2, ]
    )

multiselect2_fr = Resource(
    library,
    'js/locales/jquery-multiselect-2_fr.js',
    depends=[multiselect2, ]
    )

multiselect2_pt = Resource(
    library,
    'js/locales/jquery-multiselect-2_pt.js',
    depends=[multiselect2, ]
    )
