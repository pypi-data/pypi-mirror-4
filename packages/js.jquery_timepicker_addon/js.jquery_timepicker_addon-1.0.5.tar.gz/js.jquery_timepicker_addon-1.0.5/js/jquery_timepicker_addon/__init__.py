import fanstatic

import js.jqueryui

library = fanstatic.Library('jquery-timepicker-addon', 'resources')

timepicker_css = fanstatic.Resource(library,
    'jquery-ui-timepicker-addon.css',
    minified='jquery-ui-timepicker-addon.min.css')

timepicker_addon_js = fanstatic.Resource(library,
    'jquery-ui-timepicker-addon.js',
    minified='jquery-ui-timepicker-addon.min.js',
    depends=[js.jqueryui.ui_datepicker, js.jqueryui.ui_slider, ])

timepicker_js = fanstatic.Resource(library,
    'jquery-ui-sliderAccess.js',
    minified='jquery-ui-sliderAccess.min.js',
    depends=[timepicker_addon_js, ])

timepicker = fanstatic.Group([timepicker_css, timepicker_js])

timepicker_af = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-af.js',
    minified='localization/jquery-ui-timepicker-af.min.js',
    depends=[timepicker])

timepicker_bg = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-bg.js',
    minified='localization/jquery-ui-timepicker-bg.min.js',
    depends=[timepicker])

timepicker_ca = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ca.js',
    minified='localization/jquery-ui-timepicker-ca.min.js',
    depends=[timepicker])

timepicker_cs = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-cs.js',
    minified='localization/jquery-ui-timepicker-cs.min.js',
    depends=[timepicker])

timepicker_de = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-de.js',
    minified='localization/jquery-ui-timepicker-de.min.js',
    depends=[timepicker])

timepicker_el = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-el.js',
    minified='localization/jquery-ui-timepicker-el.min.js',
    depends=[timepicker])

timepicker_es = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-es.js',
    minified='localization/jquery-ui-timepicker-es.min.js',
    depends=[timepicker])

timepicker_et = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-et.js',
    minified='localization/jquery-ui-timepicker-et.min.js',
    depends=[timepicker])

timepicker_fi = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-fi.js',
    minified='localization/jquery-ui-timepicker-fi.min.js',
    depends=[timepicker])

timepicker_fr = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-fr.js',
    minified='localization/jquery-ui-timepicker-fr.min.js',
    depends=[timepicker])

timepicker_he = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-he.js',
    minified='localization/jquery-ui-timepicker-he.min.js',
    depends=[timepicker])

timepicker_hu = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-hu.js',
    minified='localization/jquery-ui-timepicker-hu.min.js',
    depends=[timepicker])

timepicker_id = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-id.js',
    minified='localization/jquery-ui-timepicker-id.min.js',
    depends=[timepicker])

timepicker_it = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-it.js',
    minified='localization/jquery-ui-timepicker-it.min.js',
    depends=[timepicker])

timepicker_ja = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ja.js',
    minified='localization/jquery-ui-timepicker-ja.min.js',
    depends=[timepicker])

timepicker_ko = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ko.js',
    minified='localization/jquery-ui-timepicker-ko.min.js',
    depends=[timepicker])

timepicker_nl = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-nl.js',
    minified='localization/jquery-ui-timepicker-nl.min.js',
    depends=[timepicker])

timepicker_no = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-no.js',
    minified='localization/jquery-ui-timepicker-no.min.js',
    depends=[timepicker])

timepicker_pl = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-pl.js',
    minified='localization/jquery-ui-timepicker-pl.min.js',
    depends=[timepicker])

timepicker_pt_BR = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-pt-BR.js',
    minified='localization/jquery-ui-timepicker-pt-BR.min.js',
    depends=[timepicker])

timepicker_pt = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-pt.js',
    minified='localization/jquery-ui-timepicker-pt.min.js',
    depends=[timepicker])

timepicker_ro = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ro.js',
    minified='localization/jquery-ui-timepicker-ro.min.js',
    depends=[timepicker])

timepicker_ru = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ru.js',
    minified='localization/jquery-ui-timepicker-ru.min.js',
    depends=[timepicker])

timepicker_sk = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-sk.js',
    minified='localization/jquery-ui-timepicker-sk.min.js',
    depends=[timepicker])

timepicker_tr = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-tr.js',
    minified='localization/jquery-ui-timepicker-tr.min.js',
    depends=[timepicker])

timepicker_uk = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-uk.js',
    minified='localization/jquery-ui-timepicker-uk.min.js',
    depends=[timepicker])

timepicker_vi = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-vi.js',
    minified='localization/jquery-ui-timepicker-vi.min.js',
    depends=[timepicker])


timepicker_locales = {
    "af": timepicker_af,
    "bg": timepicker_bg,
    "ca": timepicker_ca,
    "cs": timepicker_cs,
    "de": timepicker_de,
    "el": timepicker_el,
    "es": timepicker_es,
    "et": timepicker_et,
    "fi": timepicker_fi,
    "fr": timepicker_fr,
    "he": timepicker_he,
    "hu": timepicker_hu,
    "id": timepicker_id,
    "it": timepicker_it,
    "ja": timepicker_ja,
    "ko": timepicker_ko,
    "nl": timepicker_nl,
    "no": timepicker_no,
    "pl": timepicker_pl,
    "pt": timepicker_pt,
    "pt_BR": timepicker_pt_BR,
    "ro": timepicker_ro,
    "ru": timepicker_ru,
    "sk": timepicker_sk,
    "tr": timepicker_tr,
    "uk": timepicker_uk,
    "vi": timepicker_vi,
}
