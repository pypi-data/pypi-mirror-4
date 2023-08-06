import json

from ew.tests.helpers import TestCase
from ew import widget, errors, Snippet, File

class TestWidget(TestCase):

    def test_genshi_str(self):
        w = widget.Widget(
            template=Snippet('<pre>${widget}</pre>', 'genshi'))
        text = w.display()
        assert text.startswith('<pre>&lt;ew.widget.Widget object at'), text

    def test_genshi_file(self):
        w = widget.Widget(
            template=File('ew.tests.templates.simple', 'genshi'))
        text = w.display()
        assert text.startswith('<pre>&lt;ew.widget.Widget object at'), text

    def test_genshi_file_not_found(self):
        w = widget.Widget(
            template=File('ew.tests.templates.unknown', 'genshi'))
        self.assertRaises(errors.TemplateNotFound, w.display)

    def test_kajiki_str(self):
        w = widget.Widget(
            template=Snippet('<pre>${widget}</pre>', 'kajiki'))
        text = w.display()
        assert text.startswith('<pre>&lt;ew.widget.Widget object at'), text

    def test_kajiki_text_str(self):
        w = widget.Widget(
            template=Snippet('${widget}', 'kajiki-text'))
        text = w.display()
        assert text.startswith('<ew.widget.Widget object at'), text

    def test_kajiki_file(self):
        w = widget.Widget(
            template=File('ew.tests.templates.simple', 'kajiki'))
        text = w.display()
        assert text.startswith('<pre>&lt;ew.widget.Widget object at'), text

    def test_kajiki_file_not_found(self):
        w = widget.Widget(
            template=File('ew.tests.templates.unknown', 'kajiki'))
        self.assertRaises(errors.TemplateNotFound, w.display)

    def test_json(self):
        w = widget.Widget(
            template=Snippet(engine='json'))
        text = w.display()
        assert text == '{"name": null}', text

    def test_defaults(self):
        class SubWidget(widget.Widget):
            template=Snippet(engine='json')
            defaults=dict(
                widget.Widget.defaults,
                a=5,
                b=6)
        dct = json.loads(SubWidget().display())
        assert dct==dict(
            name=None, a=5, b=6), dct
        dct = json.loads(SubWidget(a=10).display())
        assert dct==dict(
            name=None, a=10, b=6), dct
        dct = json.loads(SubWidget(a=10).display(a=4))
        assert dct==dict(
            name=None, a=4, b=6), dct
