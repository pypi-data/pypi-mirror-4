from fanstatic import Library, Resource
from js.jquery import jquery
from js.jquery_form import jquery_form
from js.jquery_validate import jquery_validate
from js.jqueryui import jqueryui

library = Library('jquery-formwizard', 'resources')

jquery_formwizard = Resource(library, 'jquery.form.wizard.js',
                             minified='jquery.form.wizard.min.js',
                             depends=[jquery, jquery_form,
                                      jquery_validate, jqueryui])