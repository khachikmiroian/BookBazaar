# Generated by Django 5.1.1 on 2024-09-07 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_books_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='books',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='books/pdfs/'),
        ),
    ]