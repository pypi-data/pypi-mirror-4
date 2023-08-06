import json

from pyramid.view import view_config


@view_config(route_name="tinymce_spellchecker",
             renderer="json",
             request_method="POST")
def tinymce_spellchecker_view(request):
    """View to handle tinymce spellchecker ajax call"""
    data = json.loads(request.body)

    id_ = data['id']
    method = data['method']
    params = data['params']
    lang = params[0]
    text = params[1]

    esc = EnchantSpellChecker(lang)
    if method == 'checkWords':
        result = esc.check(text)
    elif method == 'getSuggestions':
        result = esc.suggest(text)
    else:
        raise RuntimeError("Unkown spellcheck method: '%s'" % method)

    return {
        'id': id_,
        'result': result,
        'error': None,
    }


class EnchantSpellChecker(object):

    def __init__(self, lang):
        import enchant
        self.lang = str(lang)
        if not enchant.dict_exists(lang):
            raise RuntimeError("dictionary not found for language '%s'" % lang)
        self.backend = enchant.Dict(lang)

    def check(self, text):
        return [word for word in text if word and not self.backend.check(word)]

    def suggest(self, text):
        return self.backend.suggest(text)
