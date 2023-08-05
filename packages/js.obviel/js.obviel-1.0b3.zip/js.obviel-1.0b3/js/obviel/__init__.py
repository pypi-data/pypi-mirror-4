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
    library, 'obviel-template.js')


obviel = Resource(
    library, 'obviel.js',
    depends=[jquery, json_template, obviel_template])

forms = Resource(library, 'obviel-forms.js', depends=[obviel, json2, datalink,
                                                      gettext])
forms_datepicker = Resource(library, 'obviel-forms-datepicker.js',
                            depends=[forms, jqueryui])
forms_autocomplete = Resource(library, 'obviel-forms-autocomplete.js',
                              depends=[forms, jqueryui])

patterns = Resource(library, 'obviel-patterns.js', depends=[obviel])
jgrowl = Resource(library, 'obviel-jgrowl.js', depends=[obviel, jgrowl_css,
                                                        jgrowl])
sync = Resource(library, 'obviel-sync.js', depends=[obviel])
