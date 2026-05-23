from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0007_word_last_wrong_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='next_review_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='word',
            name='review_interval_days',
            field=models.PositiveIntegerField(default=0),
        ),
    ]