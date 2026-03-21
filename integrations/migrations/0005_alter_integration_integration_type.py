# Generated migration for Sesy integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0004_alter_integration_integration_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='integration',
            name='integration_type',
            field=models.CharField(choices=[('loops', 'Loops'), ('ntfy', 'Ntfy'), ('smtp', 'Smtp'), ('mailchimp', 'Mailchimp'), ('sesy', 'Sesy')], help_text='The provider type (e.g. loops)', max_length=50),
        ),
    ]
