import unittest2 as unittest

from pyramid import testing


# TODO: those are not unittests, needs to be rewritten


class tinymce_spellcheck_viewTest(unittest.TestCase):

    def call_FUT(self, request):
        from pyramid_tinymce_spellchecker.views import tinymce_spellchecker_view
        return tinymce_spellchecker_view(request)

    def test_checkwords_empty(self):
        req = testing.DummyRequest()
        req.body = '{"id":"c0","method":"checkWords","params":["en",["Test"]]}'
        d = self.call_FUT(req)
        self.assertEquals(d, {'error': None, 'id': u'c0', 'result': []})

    def test_suggest_empty(self):
        req = testing.DummyRequest()
        req.body = '{"id":"c0","method":"getSuggestions","params":["en",["Paris"]]}'
        d = self.call_FUT(req)
        self.assertEquals(d, {
            'error': None,
            'id': u'c0',
            'result': ['Parisian', 'uproarious', 'uprising']})

    def test_unknown_method(self):
        req = testing.DummyRequest()
        req.body = '{"id":"c0","method":"foobar","params":["en",["Test"]]}'
        self.assertRaises(RuntimeError, self.call_FUT, req)

    def test_unknown_lang(self):
        req = testing.DummyRequest()
        req.body = '{"id":"c0","method":"checkWords","params":["foobar",["Test"]]}'
        self.assertRaises(RuntimeError, self.call_FUT, req)
