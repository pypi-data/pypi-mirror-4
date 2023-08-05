import os

# TODO: posts, pages, files (?)


class Page(object):
    """Represents a named or ordered post within a site."""
    def __init__(self, site, filename):
        self.site = site
        self.filename = filename

    def default_page(self):
        # TODO: implement
        return None

    def pages(self, exclude=[]):
        # TODO: implement
        return []

    def by_name(self, name):
        # TODO: implement
        return []


class Site(Page):
    """Represents a Gitpress site and its pages and sub-pages."""
    def __init__(self, working_directory=None):
        self.working_directory = os.path.abspath(os.path.normpath(working_directory))

    def __repr__(self):
        path = os.path.relpath(self.working_directory)
        return '<gitpress.Site at %s>' % repr(path)

    def posts(self):
        """Gets a list of top-level pages."""
        # TODO: implement
        return []

    def error_page(self):
        # TODO: implement
        return None
