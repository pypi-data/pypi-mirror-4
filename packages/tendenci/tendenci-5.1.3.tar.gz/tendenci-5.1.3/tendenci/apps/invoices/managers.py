from haystack.query import SearchQuerySet

from django.db.models import Manager

class InvoiceManager(Manager):
    def create_invoice(self, user, **kwargs):
        return self.create(title=kwargs.get('title', ''), 
                           estimate=kwargs.get('estimate', True),
                           status=kwargs.get('status', True), 
                           status_detail=kwargs.get('status_detail', 'estimate'),
                           object_type=kwargs.get('object_type', None),
                           object_id=kwargs.get('object_id', 0),
                           subtotal=kwargs.get('subtotal', 0),
                           total=kwargs.get('total', 0),
                           balance=kwargs.get('balance', 0),
                           creator=user, 
                           creator_username=user.username,
                           owner=user, 
                           owner_username=user.username)
        
    def search(self, query=None, *args, **kwargs):
        """
            invoice haystack to query invoices. 
            Returns a SearchQuerySet
        """
        from tendenci.apps.invoices.models import Invoice
        sqs = SearchQuerySet()
       
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        return sqs.models(Invoice)