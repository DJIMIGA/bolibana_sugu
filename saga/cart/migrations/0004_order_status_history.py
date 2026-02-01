from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_alter_cartitem_quantity'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(blank=True, choices=[('draft', 'Brouillon'), ('confirmed', 'Confirmée'), ('shipped', 'Expédiée'), ('delivered', 'Livrée'), ('cancelled', 'Annulée')], max_length=20, null=True)),
                ('new_status', models.CharField(choices=[('draft', 'Brouillon'), ('confirmed', 'Confirmée'), ('shipped', 'Expédiée'), ('delivered', 'Livrée'), ('cancelled', 'Annulée')], max_length=20)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(blank=True, max_length=50)),
                ('note', models.CharField(blank=True, max_length=255)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='cart.order')),
            ],
            options={
                'ordering': ['-changed_at'],
            },
        ),
    ]
