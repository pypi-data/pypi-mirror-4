"""
Checks settings.AUTOCOMPLETE_LIGHT_PROJECT_MODELS, expecting::

     # get_model kwargs         # list of text fields to filter on
    AUTOCOMPLETE_LIGHT_PROJECT_MODELS = (
        (('cities_light', 'city'), ['search_names']),
        (('cities_light', 'region'), ['ascii_name', 'name']),
        (('cities_light', 'country'), ['ascii_name', 'name']),
    )

And registers 'ProjectAutocomplete', an optionnal generic autocomplete that can
third party apps may decide to rely on.

This script is to be imported by autocomplete_light.autodiscover().
"""

from django.conf import settings

import autocomplete_light

try:
    setting = settings.AUTOCOMPLETE_LIGHT_PROJECT_MODELS
except AttributeError:
    pass
else:
    autocomplete = autocomplete_light.AutocompleteGenericBase

    for line in setting:
        model_class = get_model(line[0])
        search_fields = line[1]
