from gettext import gettext as _

from lxml import html
from lxml.etree import ParserError, XMLSyntaxError

from anthrax.field.text import TextField
from anthrax.widget import LongTextInput
from anthrax.exc import ValidationError

from anthrax.html_input.widget import WysiwygEditor


class HtmlField(TextField):
    widgets = [WysiwygEditor, LongTextInput]
    """Field for HTML input. Does HTML validation. Parameters:
tag_whitelist = a list of strings denoting tags or tuples (tag, args)
"""
    def to_python(self, value, form):
        try:
            return html.fromstring(value)
        except (ParserError , XMLSyntaxError) as err:
            raise ValidationError(
                _('Cannot parse. Parser message: {0}').format(err.args[0])
            )

    def from_python(self, value, form):
        if value is not None:
            return html.tostring(value).decode('utf-8')
        else:
            return ''

    def _prepare_lists(self):
        self.any_attrib_set = set()
        self.tag_attrib_dict = {}
        for tag in self.tag_whitelist:
            if isinstance(tag, tuple):
                tag, attribs = tag
                self.tag_attrib_dict[tag] = set(attribs)
            else:
                self.any_attrib_set.add(tag)

    def _validate_element(self, el):
        tag = el.tag
        if tag in self.tag_attrib_dict:
            illegal_attrs = set(el.attrib) - self.tag_attrib_dict[tag]
            if illegal_attrs:
                raise ValidationError(
                    _('Attribute {attribute} not allowed in tag {tag}').format(
                        attribute=list(illegal_attrs)[0], tag=tag
                    )
                )
        elif tag not in self.any_attrib_set:
            raise ValidationError(
                _('Tag {tag} is not allowed').format(tag=tag)
            )
        for subel in el:
            self._validate_element(subel)


    def _declarative_python_validation(self, element, form):
        self._prepare_lists()
        self._validate_element(element)
