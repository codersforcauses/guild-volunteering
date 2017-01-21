# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-21 13:42
from __future__ import unicode_literals

from django.db import migrations

#As shown here https://docs.djangoproject.com/en/1.10/ref/migration-operations/#django.db.migrations.operations.RunPython
def forwards_func(apps, schema_editor):
    Category = apps.get_model("logbook", "Category")
    db_alias = schema_editor.connection.alias
    #^(.*?)$
    #Category\(name="\1"\),
    Category.objects.using(db_alias).bulk_create([
        Category(name="Administration/Clerical"),
        Category(name="Arts/Crafts/Performing"),
        Category(name="Campaigning/Lobbying"),
        Category(name="Coaching/Umpiring"),
        Category(name="Community/Sporting Events"),
        Category(name="Counselling/Mediation/Advocacy"),
        Category(name="Disability Support Services"),
        Category(name="Education/Tutoring/Mentoring"),
        Category(name="Emergency/Safety/Rescue"),
        Category(name="Food Service"),
        Category(name="Fundraising/Retail"),
        Category(name="Gardening/Outdoor Activities"),
        Category(name="Hospital/Allied Health Assistance"),
        Category(name="Information Technology/Library Services"),
        Category(name="Marketing/Public Relations/Media"),
        Category(name="Material Relief"),
        Category(name="Professional/Management/Committee"),
        Category(name="Providing Information/Visitor Guiding"),
        Category(name="Technical/Mechanical/Maintenance"),
        Category(name="Visit/Social Support/Driving"),
        Category(name="Working with Animals"),
        Category(name="Working with Kids/Youth"),
        Category(name="Working with the Aged"),
        Category(name="Writing/Editing/Research"),
    ])

def reverse_func(apps, schema_editor):
    Category = apps.get_model("logbook", "Category")
    db_alias = schema_editor.connection.alias
    #^(.*?)$
    #Category.objects.using\(db_alias\).filter\(name="\1"\).delete\(\)
    Category.objects.using(db_alias).filter(name="Administration/Clerical").delete()
    Category.objects.using(db_alias).filter(name="Arts/Crafts/Performing").delete()
    Category.objects.using(db_alias).filter(name="Campaigning/Lobbying").delete()
    Category.objects.using(db_alias).filter(name="Coaching/Umpiring").delete()
    Category.objects.using(db_alias).filter(name="Community/Sporting Events").delete()
    Category.objects.using(db_alias).filter(name="Counselling/Mediation/Advocacy").delete()
    Category.objects.using(db_alias).filter(name="Disability Support Services").delete()
    Category.objects.using(db_alias).filter(name="Education/Tutoring/Mentoring").delete()
    Category.objects.using(db_alias).filter(name="Emergency/Safety/Rescue").delete()
    Category.objects.using(db_alias).filter(name="Food Service").delete()
    Category.objects.using(db_alias).filter(name="Fundraising/Retail").delete()
    Category.objects.using(db_alias).filter(name="Gardening/Outdoor Activities").delete()
    Category.objects.using(db_alias).filter(name="Hospital/Allied Health Assistance").delete()
    Category.objects.using(db_alias).filter(name="Information Technology/Library Services").delete()
    Category.objects.using(db_alias).filter(name="Marketing/Public Relations/Media").delete()
    Category.objects.using(db_alias).filter(name="Material Relief").delete()
    Category.objects.using(db_alias).filter(name="Professional/Management/Committee").delete()
    Category.objects.using(db_alias).filter(name="Providing Information/Visitor Guiding").delete()
    Category.objects.using(db_alias).filter(name="Technical/Mechanical/Maintenance").delete()
    Category.objects.using(db_alias).filter(name="Visit/Social Support/Driving").delete()
    Category.objects.using(db_alias).filter(name="Working with Animals").delete()
    Category.objects.using(db_alias).filter(name="Working with Kids/Youth").delete()
    Category.objects.using(db_alias).filter(name="Working with the Aged").delete()
    Category.objects.using(db_alias).filter(name="Writing/Editing/Research").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
