from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Renommer name en company_name
        migrations.RenameField(
            model_name='supplier',
            old_name='name',
            new_name='company_name',
        ),
        
        # Ajouter les nouveaux champs
        migrations.AddField(
            model_name='supplier',
            name='user',
            field=models.OneToOneField(null=True, blank=True, on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='supplier',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[MinValueValidator(0), MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='supplier',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='supplier',
            name='created_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='supplier',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
        
        # Modifier les contraintes existantes
        migrations.AlterField(
            model_name='supplier',
            name='company_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='specialty',
            field=models.CharField(blank=True, null=True, max_length=100),
        ),
    ] 