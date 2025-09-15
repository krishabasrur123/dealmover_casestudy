from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Results(models.Model):
    #min value 0.0 to ensure no negative values, max to ensure no foul amounts
    revenue= models.IntegerField(validators=[MinValueValidator(0.0), MaxValueValidator(999999999999999)]) 
    cos=models.IntegerField(validators=[MinValueValidator(0.0),MaxValueValidator(999999999999999)]) 
class financial_info(models.Model):
    period_end_date=models.DateField(default=None)
    results = models.OneToOneField(Results, on_delete= models.PROTECT)
    company=models.CharField(default=None)

