from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0002_alter_petrequest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('notif_type', models.CharField(
                    choices=[('ACCEPTED','Report Accepted'),('REJECTED','Report Rejected'),
                             ('MATCH','Possible Match Found'),('MESSAGE','Message from Admin')],
                    default='MESSAGE', max_length=20)),
                ('title',      models.CharField(max_length=200)),
                ('message',    models.TextField()),
                ('is_read',    models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pet', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='notifications',
                    to='pets.petrequest')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
