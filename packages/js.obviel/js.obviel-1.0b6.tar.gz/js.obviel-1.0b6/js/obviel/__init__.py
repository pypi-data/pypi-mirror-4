from fanstatic import Library, Resource

from js.jquery import jquery
from js.jquery_datalink import jquery_datalink as datalink
from js.jquery_jgrowl import jquery_jgrowl as jgrowl
from js.jquery_jgrowl import jquery_jgrowl_css as jgrowl_css
from js.jqueryui import jqueryui
from js.jsgettext import gettext
from js.json2 import json2
from js.json_template import json_template

library = Library('obviel', 'resources')

obviel_template = Resource(
    library, 'obviel-template.js', depends=[jquery, json2])

i18n = Resource(library, 'obviel-i18n.js', depends=[
        jquery, obviel_template, gettext])

# XXX obviel doesn't strictly use obviel_template or json_template, nor i18n,
# but then we need to make sure they get included *before* obviel core is,
# which is not possible with current Fanstatic
obviel = Resource(
    library, 'obviel.js',
    depends=[jquery, obviel_template, json_template, i18n])

forms = Resource(library, 'obviel-forms.js', depends=[
        obviel_template, obviel, json2, datalink])
forms_datepicker = Resource(library, 'obviel-forms-datepicker.js',
                            depends=[forms, jqueryui])
forms_autocomplete = Resource(library, 'obviel-forms-autocomplete.js',
                              depends=[forms, jqueryui])

def i18n_renderer(url):
    return '<link rel="i18n" href="%s" />' % url
    
forms_i18n = Resource(library, 'obviel-forms.i18n',
                      depends=[i18n],
                      renderer=i18n_renderer)

patterns = Resource(library, 'obviel-patterns.js', depends=[obviel])
jgrowl = Resource(library, 'obviel-jgrowl.js', depends=[obviel, jgrowl_css,
                                                        jgrowl])
# XXX should really depend on jshashtable & jshashset, but not packaged yet
sync = Resource(library, 'obviel-sync.js', depends=[jquery])

# XXX dependency on jquery could go away, but obviel-traject.js expects it
# currently
traject = Resource(library, 'obviel-traject.js', depends=[jquery])
