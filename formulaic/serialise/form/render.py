class HTMLGenerator:
    def _make_tag(self, tag_name, attributes=None, close=True, content=None):
        """
        Create an HTML tag with the given name and attributes.
        """
        if content is None:
            content = ''

        attrs = ""
        if attributes is not None:
            attrs = ' '.join(f'{key}="{value}"' for key, value in attributes.items())
            attrs = " " + attrs if attrs else ""

        if close:
            return f'<{tag_name}{attrs}>{content}</{tag_name}>'
        else:
            return f'<{tag_name}{attrs} />'

