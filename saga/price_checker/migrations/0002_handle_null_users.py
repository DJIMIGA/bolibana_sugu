from django.db import migrations, models
from django.conf import settings

def handle_null_users(apps, schema_editor):
    PriceEntry = apps.get_model('price_checker', 'PriceEntry')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    
    # Récupérer l'utilisateur admin par défaut
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        # Créer un utilisateur admin par défaut si nécessaire
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
    
    # Mettre à jour les entrées avec user=None
    PriceEntry.objects.filter(user__isnull=True).update(user=admin_user)

class Migration(migrations.Migration):
    dependencies = [
        ('price_checker', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(handle_null_users),
        migrations.AlterField(
            model_name='priceentry',
            name='user',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                to=settings.AUTH_USER_MODEL,
                related_name='price_entries'
            ),
        ),
    ] 