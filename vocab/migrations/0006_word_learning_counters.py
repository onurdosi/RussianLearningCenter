from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0005_word_practiced_once'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='word_list_open_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='word',
            name='practice_seen_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='word',
            name='practice_correct_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='word',
            name='practice_wrong_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='word',
            name='last_practiced_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]