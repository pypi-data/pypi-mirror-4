import os
from django.db.models import Avg, Max, Min, Count
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes import generic
from celery.task import Task
from celery.registry import tasks
from tendenci.core.exports.utils import full_model_to_dict, render_csv
from tendenci.apps.forms_builder.forms.models import Form

class FormsExportTask(Task):
    """Export Task for Celery
    This exports all forms along with their fields.
    """
    
    def run(self, **kwargs):
        """Create the xls file"""
        form_fields = [
            'title',
            'slug',
            'intro',
            'response',
            'email_text',
            'subject_template',
            'send_email',
            'email_from',
            'email_copies',
            'completion_url',
            'custom_payment',
            'payment_methods',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_member_view',
            'allow_user_edit',
            'allow_member_edit',
            'create_dt',
            'update_dt',
            'creator',
            'creator_username',
            'owner',
            'owner_username',
            'status',
            'status_detail',
        ]
        field_fields = [
            'label',
            'field_type',
            'field_function',
            'function_params',
            'required',
            'visible',
            'choices',
            'position',
            'default',
        ]
        pricing_fields = [
            'label',
            'price',
        ]
        
        forms = Form.objects.filter(status=True)
        max_fields = forms.annotate(num_fields=Count('fields')).aggregate(Max('num_fields'))['num_fields__max']
        max_pricings = forms.annotate(num_pricings=Count('pricing')).aggregate(Max('num_pricings'))['num_pricings__max']
        file_name = 'forms.csv'
        data_row_list = []
        
        for form in forms:
            data_row = []
            # form setup
            form_d = full_model_to_dict(form)
            for field in form_fields:
                if field == 'payment_methods':
                    value = [m.human_name for m in form.payment_methods.all()]
                else:
                    value = form_d[field]
                value = unicode(value).replace(os.linesep, ' ').rstrip()
                data_row.append(value)
                
            if form.fields.all():
                # field setup
                for field in form.fields.all():
                    field_d = full_model_to_dict(field)
                    for f in field_fields:
                        value = field_d[f]
                        value = unicode(value).replace(os.linesep, ' ').rstrip()
                        data_row.append(value)
            
            # fill out the rest of the field columns
            if form.fields.all().count() < max_fields:
                for i in range(0, max_fields - form.fields.all().count()):
                    for f in field_fields:
                        data_row.append('')
                        
            if form.pricing_set.all():
                # field setup
                for pricing in form.pricing_set.all():
                    pricing_d = full_model_to_dict(pricing)
                    for f in pricing_fields:
                        value = pricing_d[f]
                        value = unicode(value).replace(os.linesep, ' ').rstrip()
                        data_row.append(value)
            
            # fill out the rest of the field columns
            if form.pricing_set.all().count() < max_pricings:
                for i in range(0, max_pricings - form.pricing_set.all().count()):
                    for f in pricing_fields:
                        data_row.append('')
            
            data_row_list.append(data_row)
        
        fields = form_fields
        for i in range(0, max_fields):
            fields = fields + ["field %s %s" % (i, f) for f in field_fields]
        for i in range(0, max_pricings):
            fields = fields + ["pricing %s %s" % (i, f) for f in pricing_fields]
        return render_csv(file_name, fields, data_row_list)
