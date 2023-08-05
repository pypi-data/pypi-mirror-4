from fanstatic import Library, Resource
import js.jquery

# This code is auto-generated and not PEP8 compliant

library = Library('jqueryui', 'resources')

ui_core = Resource(library, 'ui/jquery.ui.core.js', depends=[js.jquery.jquery], minified='ui/minified/jquery.ui.core.min.js')
ui_datepicker = Resource(library, 'ui/jquery.ui.datepicker.js', depends=[ui_core], minified='ui/minified/jquery.ui.datepicker.min.js')
ui_position = Resource(library, 'ui/jquery.ui.position.js', depends=[js.jquery.jquery], minified='ui/minified/jquery.ui.position.min.js')
ui_widget = Resource(library, 'ui/jquery.ui.widget.js', depends=[js.jquery.jquery], minified='ui/minified/jquery.ui.widget.min.js')
ui_accordion = Resource(library, 'ui/jquery.ui.accordion.js', depends=[ui_core, ui_widget], minified='ui/minified/jquery.ui.accordion.min.js')
ui_autocomplete = Resource(library, 'ui/jquery.ui.autocomplete.js', depends=[ui_core, ui_position, ui_widget], minified='ui/minified/jquery.ui.autocomplete.min.js')
ui_button = Resource(library, 'ui/jquery.ui.button.js', depends=[ui_core, ui_widget], minified='ui/minified/jquery.ui.button.min.js')
ui_dialog = Resource(library, 'ui/jquery.ui.dialog.js', depends=[ui_core, ui_position, ui_widget], minified='ui/minified/jquery.ui.dialog.min.js')
ui_mouse = Resource(library, 'ui/jquery.ui.mouse.js', depends=[ui_core, ui_widget], minified='ui/minified/jquery.ui.mouse.min.js')
ui_draggable = Resource(library, 'ui/jquery.ui.draggable.js', depends=[ui_core, ui_mouse, ui_widget], minified='ui/minified/jquery.ui.draggable.min.js')
ui_droppable = Resource(library, 'ui/jquery.ui.droppable.js', depends=[ui_core, ui_draggable, ui_mouse, ui_widget], minified='ui/minified/jquery.ui.droppable.min.js')
ui_progressbar = Resource(library, 'ui/jquery.ui.progressbar.js', depends=[ui_core, ui_widget], minified='ui/minified/jquery.ui.progressbar.min.js')
ui_resizable = Resource(library, 'ui/jquery.ui.resizable.js', depends=[ui_core, ui_mouse, ui_widget], minified='ui/minified/jquery.ui.resizable.min.js')
ui_selectable = Resource(library, 'ui/jquery.ui.selectable.js', depends=[ui_core, ui_mouse, ui_widget], minified='ui/minified/jquery.ui.selectable.min.js')
ui_slider = Resource(library, 'ui/jquery.ui.slider.js', depends=[ui_core, ui_mouse, ui_widget], minified='ui/minified/jquery.ui.slider.min.js')
ui_sortable = Resource(library, 'ui/jquery.ui.sortable.js', depends=[ui_core, ui_mouse, ui_widget], minified='ui/minified/jquery.ui.sortable.min.js')
ui_tabs = Resource(library, 'ui/jquery.ui.tabs.js', depends=[ui_core, ui_widget], minified='ui/minified/jquery.ui.tabs.min.js')

effects_core = Resource(library, 'ui/jquery.effects.core.js', depends=[js.jquery.jquery], minified='ui/minified/jquery.effects.core.min.js')
effects_blind = Resource(library, 'ui/jquery.effects.blind.js', depends=[effects_core], minified='ui/minified/jquery.effects.blind.min.js')
effects_bounce = Resource(library, 'ui/jquery.effects.bounce.js', depends=[effects_core], minified='ui/minified/jquery.effects.bounce.min.js')
effects_clip = Resource(library, 'ui/jquery.effects.clip.js', depends=[effects_core], minified='ui/minified/jquery.effects.clip.min.js')
effects_drop = Resource(library, 'ui/jquery.effects.drop.js', depends=[effects_core], minified='ui/minified/jquery.effects.drop.min.js')
effects_explode = Resource(library, 'ui/jquery.effects.explode.js', depends=[effects_core], minified='ui/minified/jquery.effects.explode.min.js')
effects_fade = Resource(library, 'ui/jquery.effects.fade.js', depends=[effects_core], minified='ui/minified/jquery.effects.fade.min.js')
effects_fold = Resource(library, 'ui/jquery.effects.fold.js', depends=[effects_core], minified='ui/minified/jquery.effects.fold.min.js')
effects_highlight = Resource(library, 'ui/jquery.effects.highlight.js', depends=[effects_core], minified='ui/minified/jquery.effects.highlight.min.js')
effects_pulsate = Resource(library, 'ui/jquery.effects.pulsate.js', depends=[effects_core], minified='ui/minified/jquery.effects.pulsate.min.js')
effects_scale = Resource(library, 'ui/jquery.effects.scale.js', depends=[effects_core], minified='ui/minified/jquery.effects.scale.min.js')
effects_shake = Resource(library, 'ui/jquery.effects.shake.js', depends=[effects_core], minified='ui/minified/jquery.effects.shake.min.js')
effects_slide = Resource(library, 'ui/jquery.effects.slide.js', depends=[effects_core], minified='ui/minified/jquery.effects.slide.min.js')
effects_transfer = Resource(library, 'ui/jquery.effects.transfer.js', depends=[effects_core], minified='ui/minified/jquery.effects.transfer.min.js')

jqueryui = Resource(library, 'ui/jquery-ui.js', depends=[js.jquery.jquery], minified='ui/minified/jquery-ui.min.js', supersedes=[effects_blind, effects_bounce, effects_clip, effects_core, effects_drop, effects_explode, effects_fade, effects_fold, effects_highlight, effects_pulsate, effects_scale, effects_shake, effects_slide, effects_transfer, ui_accordion, ui_autocomplete, ui_button, ui_core, ui_datepicker, ui_dialog, ui_draggable, ui_droppable, ui_mouse, ui_position, ui_progressbar, ui_resizable, ui_selectable, ui_slider, ui_sortable, ui_tabs, ui_widget])

base = Resource(library, 'themes/base/jquery-ui.css', minified='themes/base/jquery-ui.min.css')
black_tie = Resource(library, 'themes/black-tie/jquery-ui.css', minified='themes/black-tie/jquery-ui.min.css')
blitzer = Resource(library, 'themes/blitzer/jquery-ui.css', minified='themes/blitzer/jquery-ui.min.css')
bootstrap = Resource(library, 'themes/bootstrap/jquery-ui.css', minified='themes/bootstrap/jquery-ui.min.css')
cupertino = Resource(library, 'themes/cupertino/jquery-ui.css', minified='themes/cupertino/jquery-ui.min.css')
dark_hive = Resource(library, 'themes/dark-hive/jquery-ui.css', minified='themes/dark-hive/jquery-ui.min.css')
dot_luv = Resource(library, 'themes/dot-luv/jquery-ui.css', minified='themes/dot-luv/jquery-ui.min.css')
eggplant = Resource(library, 'themes/eggplant/jquery-ui.css', minified='themes/eggplant/jquery-ui.min.css')
excite_bike = Resource(library, 'themes/excite-bike/jquery-ui.css', minified='themes/excite-bike/jquery-ui.min.css')
flick = Resource(library, 'themes/flick/jquery-ui.css', minified='themes/flick/jquery-ui.min.css')
hot_sneaks = Resource(library, 'themes/hot-sneaks/jquery-ui.css', minified='themes/hot-sneaks/jquery-ui.min.css')
humanity = Resource(library, 'themes/humanity/jquery-ui.css', minified='themes/humanity/jquery-ui.min.css')
le_frog = Resource(library, 'themes/le-frog/jquery-ui.css', minified='themes/le-frog/jquery-ui.min.css')
mint_choc = Resource(library, 'themes/mint-choc/jquery-ui.css', minified='themes/mint-choc/jquery-ui.min.css')
overcast = Resource(library, 'themes/overcast/jquery-ui.css', minified='themes/overcast/jquery-ui.min.css')
pepper_grinder = Resource(library, 'themes/pepper-grinder/jquery-ui.css', minified='themes/pepper-grinder/jquery-ui.min.css')
redmond = Resource(library, 'themes/redmond/jquery-ui.css', minified='themes/redmond/jquery-ui.min.css')
smoothness = Resource(library, 'themes/smoothness/jquery-ui.css', minified='themes/smoothness/jquery-ui.min.css')
south_street = Resource(library, 'themes/south-street/jquery-ui.css', minified='themes/south-street/jquery-ui.min.css')
start = Resource(library, 'themes/start/jquery-ui.css', minified='themes/start/jquery-ui.min.css')
sunny = Resource(library, 'themes/sunny/jquery-ui.css', minified='themes/sunny/jquery-ui.min.css')
swanky_purse = Resource(library, 'themes/swanky-purse/jquery-ui.css', minified='themes/swanky-purse/jquery-ui.min.css')
trontastic = Resource(library, 'themes/trontastic/jquery-ui.css', minified='themes/trontastic/jquery-ui.min.css')
ui_darkness = Resource(library, 'themes/ui-darkness/jquery-ui.css', minified='themes/ui-darkness/jquery-ui.min.css')
ui_lightness = Resource(library, 'themes/ui-lightness/jquery-ui.css', minified='themes/ui-lightness/jquery-ui.min.css')
vader = Resource(library, 'themes/vader/jquery-ui.css', minified='themes/vader/jquery-ui.min.css')

ui_datepicker_af = Resource(library, 'ui/i18n/jquery.ui.datepicker-af.js', depends=[ui_datepicker])
ui_datepicker_ar = Resource(library, 'ui/i18n/jquery.ui.datepicker-ar.js', depends=[ui_datepicker])
ui_datepicker_ar_DZ = Resource(library, 'ui/i18n/jquery.ui.datepicker-ar-DZ.js', depends=[ui_datepicker])
ui_datepicker_az = Resource(library, 'ui/i18n/jquery.ui.datepicker-az.js', depends=[ui_datepicker])
ui_datepicker_bg = Resource(library, 'ui/i18n/jquery.ui.datepicker-bg.js', depends=[ui_datepicker])
ui_datepicker_bs = Resource(library, 'ui/i18n/jquery.ui.datepicker-bs.js', depends=[ui_datepicker])
ui_datepicker_ca = Resource(library, 'ui/i18n/jquery.ui.datepicker-ca.js', depends=[ui_datepicker])
ui_datepicker_cs = Resource(library, 'ui/i18n/jquery.ui.datepicker-cs.js', depends=[ui_datepicker])
ui_datepicker_cy_GB = Resource(library, 'ui/i18n/jquery.ui.datepicker-cy-GB.js', depends=[ui_datepicker])
ui_datepicker_da = Resource(library, 'ui/i18n/jquery.ui.datepicker-da.js', depends=[ui_datepicker])
ui_datepicker_de = Resource(library, 'ui/i18n/jquery.ui.datepicker-de.js', depends=[ui_datepicker])
ui_datepicker_el = Resource(library, 'ui/i18n/jquery.ui.datepicker-el.js', depends=[ui_datepicker])
ui_datepicker_en_AU = Resource(library, 'ui/i18n/jquery.ui.datepicker-en-AU.js', depends=[ui_datepicker])
ui_datepicker_en_GB = Resource(library, 'ui/i18n/jquery.ui.datepicker-en-GB.js', depends=[ui_datepicker])
ui_datepicker_en_NZ = Resource(library, 'ui/i18n/jquery.ui.datepicker-en-NZ.js', depends=[ui_datepicker])
ui_datepicker_eo = Resource(library, 'ui/i18n/jquery.ui.datepicker-eo.js', depends=[ui_datepicker])
ui_datepicker_es = Resource(library, 'ui/i18n/jquery.ui.datepicker-es.js', depends=[ui_datepicker])
ui_datepicker_et = Resource(library, 'ui/i18n/jquery.ui.datepicker-et.js', depends=[ui_datepicker])
ui_datepicker_eu = Resource(library, 'ui/i18n/jquery.ui.datepicker-eu.js', depends=[ui_datepicker])
ui_datepicker_fa = Resource(library, 'ui/i18n/jquery.ui.datepicker-fa.js', depends=[ui_datepicker])
ui_datepicker_fi = Resource(library, 'ui/i18n/jquery.ui.datepicker-fi.js', depends=[ui_datepicker])
ui_datepicker_fo = Resource(library, 'ui/i18n/jquery.ui.datepicker-fo.js', depends=[ui_datepicker])
ui_datepicker_fr = Resource(library, 'ui/i18n/jquery.ui.datepicker-fr.js', depends=[ui_datepicker])
ui_datepicker_fr_CH = Resource(library, 'ui/i18n/jquery.ui.datepicker-fr-CH.js', depends=[ui_datepicker])
ui_datepicker_gl = Resource(library, 'ui/i18n/jquery.ui.datepicker-gl.js', depends=[ui_datepicker])
ui_datepicker_he = Resource(library, 'ui/i18n/jquery.ui.datepicker-he.js', depends=[ui_datepicker])
ui_datepicker_hi = Resource(library, 'ui/i18n/jquery.ui.datepicker-hi.js', depends=[ui_datepicker])
ui_datepicker_hr = Resource(library, 'ui/i18n/jquery.ui.datepicker-hr.js', depends=[ui_datepicker])
ui_datepicker_hu = Resource(library, 'ui/i18n/jquery.ui.datepicker-hu.js', depends=[ui_datepicker])
ui_datepicker_hy = Resource(library, 'ui/i18n/jquery.ui.datepicker-hy.js', depends=[ui_datepicker])
ui_datepicker_id = Resource(library, 'ui/i18n/jquery.ui.datepicker-id.js', depends=[ui_datepicker])
ui_datepicker_is = Resource(library, 'ui/i18n/jquery.ui.datepicker-is.js', depends=[ui_datepicker])
ui_datepicker_it = Resource(library, 'ui/i18n/jquery.ui.datepicker-it.js', depends=[ui_datepicker])
ui_datepicker_ja = Resource(library, 'ui/i18n/jquery.ui.datepicker-ja.js', depends=[ui_datepicker])
ui_datepicker_ka = Resource(library, 'ui/i18n/jquery.ui.datepicker-ka.js', depends=[ui_datepicker])
ui_datepicker_kk = Resource(library, 'ui/i18n/jquery.ui.datepicker-kk.js', depends=[ui_datepicker])
ui_datepicker_km = Resource(library, 'ui/i18n/jquery.ui.datepicker-km.js', depends=[ui_datepicker])
ui_datepicker_ko = Resource(library, 'ui/i18n/jquery.ui.datepicker-ko.js', depends=[ui_datepicker])
ui_datepicker_kz = Resource(library, 'ui/i18n/jquery.ui.datepicker-kz.js', depends=[ui_datepicker])
ui_datepicker_lb = Resource(library, 'ui/i18n/jquery.ui.datepicker-lb.js', depends=[ui_datepicker])
ui_datepicker_lt = Resource(library, 'ui/i18n/jquery.ui.datepicker-lt.js', depends=[ui_datepicker])
ui_datepicker_lv = Resource(library, 'ui/i18n/jquery.ui.datepicker-lv.js', depends=[ui_datepicker])
ui_datepicker_mk = Resource(library, 'ui/i18n/jquery.ui.datepicker-mk.js', depends=[ui_datepicker])
ui_datepicker_ml = Resource(library, 'ui/i18n/jquery.ui.datepicker-ml.js', depends=[ui_datepicker])
ui_datepicker_ms = Resource(library, 'ui/i18n/jquery.ui.datepicker-ms.js', depends=[ui_datepicker])
ui_datepicker_nl = Resource(library, 'ui/i18n/jquery.ui.datepicker-nl.js', depends=[ui_datepicker])
ui_datepicker_nl_BE = Resource(library, 'ui/i18n/jquery.ui.datepicker-nl-BE.js', depends=[ui_datepicker])
ui_datepicker_no = Resource(library, 'ui/i18n/jquery.ui.datepicker-no.js', depends=[ui_datepicker])
ui_datepicker_pl = Resource(library, 'ui/i18n/jquery.ui.datepicker-pl.js', depends=[ui_datepicker])
ui_datepicker_pt = Resource(library, 'ui/i18n/jquery.ui.datepicker-pt.js', depends=[ui_datepicker])
ui_datepicker_pt_BR = Resource(library, 'ui/i18n/jquery.ui.datepicker-pt-BR.js', depends=[ui_datepicker])
ui_datepicker_rm = Resource(library, 'ui/i18n/jquery.ui.datepicker-rm.js', depends=[ui_datepicker])
ui_datepicker_ro = Resource(library, 'ui/i18n/jquery.ui.datepicker-ro.js', depends=[ui_datepicker])
ui_datepicker_ru = Resource(library, 'ui/i18n/jquery.ui.datepicker-ru.js', depends=[ui_datepicker])
ui_datepicker_sk = Resource(library, 'ui/i18n/jquery.ui.datepicker-sk.js', depends=[ui_datepicker])
ui_datepicker_sl = Resource(library, 'ui/i18n/jquery.ui.datepicker-sl.js', depends=[ui_datepicker])
ui_datepicker_sq = Resource(library, 'ui/i18n/jquery.ui.datepicker-sq.js', depends=[ui_datepicker])
ui_datepicker_sr = Resource(library, 'ui/i18n/jquery.ui.datepicker-sr.js', depends=[ui_datepicker])
ui_datepicker_sr_SR = Resource(library, 'ui/i18n/jquery.ui.datepicker-sr-SR.js', depends=[ui_datepicker])
ui_datepicker_sv = Resource(library, 'ui/i18n/jquery.ui.datepicker-sv.js', depends=[ui_datepicker])
ui_datepicker_ta = Resource(library, 'ui/i18n/jquery.ui.datepicker-ta.js', depends=[ui_datepicker])
ui_datepicker_th = Resource(library, 'ui/i18n/jquery.ui.datepicker-th.js', depends=[ui_datepicker])
ui_datepicker_tj = Resource(library, 'ui/i18n/jquery.ui.datepicker-tj.js', depends=[ui_datepicker])
ui_datepicker_tr = Resource(library, 'ui/i18n/jquery.ui.datepicker-tr.js', depends=[ui_datepicker])
ui_datepicker_uk = Resource(library, 'ui/i18n/jquery.ui.datepicker-uk.js', depends=[ui_datepicker])
ui_datepicker_vi = Resource(library, 'ui/i18n/jquery.ui.datepicker-vi.js', depends=[ui_datepicker])
ui_datepicker_zh_CN = Resource(library, 'ui/i18n/jquery.ui.datepicker-zh-CN.js', depends=[ui_datepicker])
ui_datepicker_zh_HK = Resource(library, 'ui/i18n/jquery.ui.datepicker-zh-HK.js', depends=[ui_datepicker])
ui_datepicker_zh_TW = Resource(library, 'ui/i18n/jquery.ui.datepicker-zh-TW.js', depends=[ui_datepicker])
jqueryui_i18n = Resource(library, 'ui/i18n/jquery-ui-i18n.js', depends=[ui_datepicker], supersedes=[ui_datepicker_af, ui_datepicker_ar, ui_datepicker_ar_DZ, ui_datepicker_az, ui_datepicker_bg, ui_datepicker_bs, ui_datepicker_ca, ui_datepicker_cs, ui_datepicker_da, ui_datepicker_de, ui_datepicker_el, ui_datepicker_en_AU, ui_datepicker_en_GB, ui_datepicker_en_NZ, ui_datepicker_eo, ui_datepicker_es, ui_datepicker_et, ui_datepicker_eu, ui_datepicker_fa, ui_datepicker_fi, ui_datepicker_fo, ui_datepicker_fr, ui_datepicker_fr_CH, ui_datepicker_gl, ui_datepicker_he, ui_datepicker_hr, ui_datepicker_hu, ui_datepicker_hy, ui_datepicker_id, ui_datepicker_is, ui_datepicker_it, ui_datepicker_ja, ui_datepicker_ko, ui_datepicker_kz, ui_datepicker_lt, ui_datepicker_lv, ui_datepicker_ml, ui_datepicker_ms, ui_datepicker_nl, ui_datepicker_no, ui_datepicker_pl, ui_datepicker_pt, ui_datepicker_pt_BR, ui_datepicker_rm, ui_datepicker_ro, ui_datepicker_ru, ui_datepicker_sk, ui_datepicker_sl, ui_datepicker_sq, ui_datepicker_sr, ui_datepicker_sr_SR, ui_datepicker_sv, ui_datepicker_ta, ui_datepicker_th, ui_datepicker_tj, ui_datepicker_tr, ui_datepicker_uk, ui_datepicker_vi, ui_datepicker_zh_CN, ui_datepicker_zh_HK, ui_datepicker_zh_TW, ui_datepicker_cy_GB, ui_datepicker_hi, ui_datepicker_ka, ui_datepicker_kk, ui_datepicker_km, ui_datepicker_lb, ui_datepicker_mk, ui_datepicker_nl_BE])

ui_datepicker_locales = {
    "af": ui_datepicker_af,
    "ar": ui_datepicker_ar,
    "ar_DZ": ui_datepicker_ar_DZ,
    "az": ui_datepicker_az,
    "bg": ui_datepicker_bg,
    "bs": ui_datepicker_bs,
    "ca": ui_datepicker_ca,
    "cs": ui_datepicker_cs,
    "cy_GB": ui_datepicker_cy_GB,
    "da": ui_datepicker_da,
    "de": ui_datepicker_de,
    "el": ui_datepicker_el,
    "en_AU": ui_datepicker_en_AU,
    "en_GB": ui_datepicker_en_GB,
    "en_NZ": ui_datepicker_en_NZ,
    "eo": ui_datepicker_eo,
    "es": ui_datepicker_es,
    "et": ui_datepicker_et,
    "eu": ui_datepicker_eu,
    "fa": ui_datepicker_fa,
    "fi": ui_datepicker_fi,
    "fo": ui_datepicker_fo,
    "fr": ui_datepicker_fr,
    "fr_CH": ui_datepicker_fr_CH,
    "gl": ui_datepicker_gl,
    "he": ui_datepicker_he,
    "hi": ui_datepicker_hi,
    "hr": ui_datepicker_hr,
    "hu": ui_datepicker_hu,
    "hy": ui_datepicker_hy,
    "id": ui_datepicker_id,
    "is": ui_datepicker_is,
    "it": ui_datepicker_it,
    "ja": ui_datepicker_ja,
    "ka": ui_datepicker_ka,
    "kk": ui_datepicker_kk,
    "km": ui_datepicker_km,
    "ko": ui_datepicker_ko,
    "kz": ui_datepicker_kz,
    "lb": ui_datepicker_lb,
    "lt": ui_datepicker_lt,
    "lv": ui_datepicker_lv,
    "mk": ui_datepicker_mk,
    "ml": ui_datepicker_ml,
    "ms": ui_datepicker_ms,
    "nl": ui_datepicker_nl,
    "nl_BE": ui_datepicker_nl_BE,
    "no": ui_datepicker_no,
    "pl": ui_datepicker_pl,
    "pt": ui_datepicker_pt,
    "pt_BR": ui_datepicker_pt_BR,
    "rm": ui_datepicker_rm,
    "ro": ui_datepicker_ro,
    "ru": ui_datepicker_ru,
    "sk": ui_datepicker_sk,
    "sl": ui_datepicker_sl,
    "sq": ui_datepicker_sq,
    "sr": ui_datepicker_sr,
    "sr_SR": ui_datepicker_sr_SR,
    "sv": ui_datepicker_sv,
    "ta": ui_datepicker_ta,
    "th": ui_datepicker_th,
    "tj": ui_datepicker_tj,
    "tr": ui_datepicker_tr,
    "uk": ui_datepicker_uk,
    "vi": ui_datepicker_vi,
    "zh_CN": ui_datepicker_zh_CN,
    "zh_HK": ui_datepicker_zh_HK,
    "zh_TW": ui_datepicker_zh_TW,
}
