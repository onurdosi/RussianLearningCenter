from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0006_word_learning_counters'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='last_wrong_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]