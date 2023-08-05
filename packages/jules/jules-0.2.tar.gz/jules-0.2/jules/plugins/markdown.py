from jules.plugins import ContentPlugin

from markdown import markdown


class MarkdownContentParser(ContentPlugin):
    """Parses any .md files in a bundle."""

    extensions = ('.md', '.markdown')

    def parse_string(self, src):
        return markdown(src)
