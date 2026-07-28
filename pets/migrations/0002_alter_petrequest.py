from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='petrequest',
            name='admin_note',
            field=models.TextField(blank=True, help_text='Optional note shown to the user about this decision'),
        ),
        migrations.AddField(
            model_name='petrequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='petrequest',
            name='status',
            field=models.CharField(
                choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')],
                default='PENDING',
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='petrequest',
            name='pet_type',
            field=models.CharField(
                choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Bird', 'Bird'), ('Rabbit', 'Rabbit'), ('Other', 'Other')],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name='petrequest',
            name='breed',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterModelOptions(
            name='petrequest',
            options={'ordering': ['-created_at']},
        ),
    ]
