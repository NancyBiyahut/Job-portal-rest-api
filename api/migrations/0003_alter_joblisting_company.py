# Generated by Django 4.1.4 on 2024-03-07 04:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_remove_joblisting_posted_by_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="joblisting",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.employer"
            ),
        ),
    ]
