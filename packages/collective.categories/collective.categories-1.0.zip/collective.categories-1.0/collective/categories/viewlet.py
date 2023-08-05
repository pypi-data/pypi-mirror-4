from plone.app.layout.viewlets import common
from collective.categories.backend import get_backend


class Categories(common.ViewletBase):
    """Display categories"""
    def update(self):
        super(Categories, self).update()
        backend = get_backend(self.context)
        self.categories = backend.get_categories()
