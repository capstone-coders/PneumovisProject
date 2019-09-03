from django.db import models

# Create your models here.

class database(models.Model):
    id = models.AutoField(primary_key=True)
    Patient_ID = models.TextField()
    Barcode = models.TextField()
    Week = models.TextField()
    npa_a4_growth = models.TextField(default='')
    DateCollection = models.TextField(default='')
    Presence = models.TextField(default='')
    dob = models.TextField(default='')
    sex = models.TextField(default='')
    HIVexpose = models.TextField(default='')
    site = models.TextField(default='')
    Disease = models.TextField(default='')
    Serotype = models.TextField(default='')
    vaccine_status = models.TextField(default='')
    Sequence_Type = models.TextField(default='')

    class Meta:
        db_table = 'PneumoVis'

    def __str__(self):
        return self.Patient_ID

    def __unicode__(self):
        return u'%s %s' % (self.sex, self.id)
