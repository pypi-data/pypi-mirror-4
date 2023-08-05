from django.utils.timezone import now
from django.db.models import Manager


class PublicManager(Manager):

    def public(self):
        """Return public posts."""
        return self.get_query_set().filter(status__gte=2)

    def published(self):
        """Return public posts that are not in the future."""
        return self.get_query_set().filter(status__gte=2, publish__lte=now())
