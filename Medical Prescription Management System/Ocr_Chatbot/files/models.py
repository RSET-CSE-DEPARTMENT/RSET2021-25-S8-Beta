from django.db import models
from django import forms

class register(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    password = models.CharField(max_length=150)

class tbl_document(models.Model):
    name = models.CharField(max_length=150)
    documents = models.CharField(max_length=150)
    user_id = models.CharField(max_length=150)
    doc_name = models.CharField(max_length=150)

    
    
class feedback(models.Model):
    user_id = models.CharField(max_length=150)
    description = models.CharField(max_length=150)
     


class tbl_text(models.Model):
    user_id = models.CharField(max_length=150)
    text_file = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    text_name = models.CharField(max_length=150)
    
        