from django.db import models
import json

# Create your models here.
class LDA(models.Model):
    id = models.AutoField(primary_key=True)
    startingDate = models.DateTimeField()
    endingDate = models.DateTimeField(null=True)
    duration =  models.DecimalField(max_digits=10, decimal_places=3, null=True)
    numTopics =  models.DecimalField(max_digits=10, decimal_places=3)
    status = models.CharField(max_length=300)
    corpusFile = models.CharField(max_length=500)
    outputFile = models.CharField(max_length=500, null=True)
    HTMLoutputFile = models.CharField(max_length=500, null=True)
    topic = models.CharField(max_length=50)
    coherence =  models.DecimalField(max_digits=10, decimal_places=3, null=True)
    error = models.CharField(max_length=5000, null=True)

class bertopic(models.Model):
    id = models.AutoField(primary_key=True)
    startingDate = models.DateTimeField()
    endingDate = models.DateTimeField(null=True)
    duration =  models.DecimalField(max_digits=10, decimal_places=3, null=True)
    numTopics =  models.DecimalField(max_digits=10, decimal_places=3)
    status = models.CharField(max_length=300)
    corpusFile = models.CharField(max_length=500)
    outputFile = models.CharField(max_length=500, null=True)
    HTMLoutputFile = models.CharField(max_length=500, null=True)
    topic = models.CharField(max_length=50)
    coherence =  models.DecimalField(max_digits=10, decimal_places=3, null=True)
    error = models.CharField(max_length=5000, null=True)

class FAQ(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=50)
    question = models.TextField()
    answer = models.TextField()

class Interview(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=50)
    active = models.BooleanField()
    respect_order = models.BooleanField()
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question = models.TextField()
    topic = models.CharField(max_length=50)
    conclusion = models.TextField(default=None)
    question_order = models.IntegerField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Reflection(models.Model):
    id = models.AutoField(primary_key=True)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    reflection = models.TextField()
    conditions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_conditions(self, conditions_dict):
        self.conditions = json.dumps(conditions_dict)

    def get_conditions(self):
        return json.loads(self.conditions)