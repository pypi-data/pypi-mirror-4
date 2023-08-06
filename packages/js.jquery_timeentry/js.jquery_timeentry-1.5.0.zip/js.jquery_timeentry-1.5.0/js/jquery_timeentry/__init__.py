from fanstatic import Library, Resource
import js.jquery

library = Library('jquery_time_entry', 'resources')

time_entry = Resource(
    library, 'jquery.timeentry.js',
    minified='jquery.timeentry.min.js',
    depends=[
        Resource(library, 'jquery.timeentry.css'),
        js.jquery.jquery
    ])

time_entry_de = Resource(
    library, 'jquery.timeentry-de.js',
    depends=[time_entry])

time_entry_es = Resource(
    library, 'jquery.timeentry-es.js',
    depends=[time_entry])

time_entry_nl = Resource(
    library, 'jquery.timeentry-nl.js',
    depends=[time_entry])

time_entry_ca = Resource(
    library, 'jquery.timeentry-ca.js',
    depends=[time_entry])

time_entry_cs = Resource(
    library, 'jquery.timeentry-cs.js',
    depends=[time_entry])

time_entry_fa = Resource(
    library, 'jquery.timeentry-fa.js',
    depends=[time_entry])

time_entry_fr = Resource(
    library, 'jquery.timeentry-fr.js',
    depends=[time_entry])

time_entry_hu = Resource(
    library, 'jquery.timeentry-hu.js',
    depends=[time_entry])

time_entry_is = Resource(
    library, 'jquery.timeentry-is.js',
    depends=[time_entry])

time_entry_it = Resource(
    library, 'jquery.timeentry-it.js',
    depends=[time_entry])

time_entry_ja = Resource(
    library, 'jquery.timeentry-ja.js',
    depends=[time_entry])

time_entry_lt = Resource(
    library, 'jquery.timeentry-lt.js',
    depends=[time_entry])

time_entry_lv = Resource(
    library, 'jquery.timeentry-lv.js',
    depends=[time_entry])

time_entry_pl = Resource(
    library, 'jquery.timeentry-pl.js',
    depends=[time_entry])

time_entry_pt = Resource(
    library, 'jquery.timeentry-pt.js',
    depends=[time_entry])

time_entry_ro = Resource(
    library, 'jquery.timeentry-ro.js',
    depends=[time_entry])

time_entry_ru = Resource(
    library, 'jquery.timeentry-ru.js',
    depends=[time_entry])

time_entry_sk = Resource(
    library, 'jquery.timeentry-sk.js',
    depends=[time_entry])

time_entry_sv = Resource(
    library, 'jquery.timeentry-sv.js',
    depends=[time_entry])

time_entry_tr = Resource(
    library, 'jquery.timeentry-tr.js',
    depends=[time_entry])

time_entry_vi = Resource(
    library, 'jquery.timeentry-vi.js',
    depends=[time_entry])

time_entry_zh_cn = Resource(
    library, 'jquery.timeentry-zh-CN.js',
    depends=[time_entry])

time_entry_zh_tw = Resource(
    library, 'jquery.timeentry-zh-TW.js',
    depends=[time_entry])
