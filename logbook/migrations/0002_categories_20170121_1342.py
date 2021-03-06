# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-21 13:42
from __future__ import unicode_literals

from django.db import migrations

cats = [
    "Administration/Clerical",
    "Arts/Crafts/Performing",
    "Campaigning/Lobbying",
    "Coaching/Umpiring",
    "Community/Sporting Events",
    "Counselling/Mediation/Advocacy",
    "Disability Support Services",
    "Education/Tutoring/Mentoring",
    "Emergency/Safety/Rescue",
    "Food Service",
    "Fundraising/Retail",
    "Gardening/Outdoor Activities",
    "Hospital/Allied Health Assistance",
    "Information Technology/Library Services",
    "Marketing/Public Relations/Media",
    "Material Relief",
    "Professional/Management/Committee",
    "Providing Information/Visitor Guiding",
    "Technical/Mechanical/Maintenance",
    "Visit/Social Support/Driving",
    "Working with Animals",
    "Working with Kids/Youth",
    "Working with the Aged",
    "Writing/Editing/Research"
]

#As shown here https://docs.djangoproject.com/en/1.10/ref/migration-operations/#django.db.migrations.operations.RunPython
def forwards_func(apps, schema_editor):
    Category = apps.get_model("logbook", "Category")
    db_alias = schema_editor.connection.alias
    Category.objects.using(db_alias).bulk_create([Category(name=cat) for cat in cats])

def reverse_func(apps, schema_editor):
    Category = apps.get_model("logbook", "Category")
    db_alias = schema_editor.connection.alias
    for cat in cats:
        Category.objects.using(db_alias).filter(name=cat).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
