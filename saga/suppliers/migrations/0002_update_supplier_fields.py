from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='supplier',
            old_name='name',
            new_name='company_name',
        ),
        migrations.AddField(
            model_name='supplier',
            name='user',
            field=models.OneToOneField(null=True, blank=True, on_delete=models.CASCADE, to='accounts.shopper'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='suppliers/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='specialty',
            field=models.CharField(blank=True, choices=[('Fournisseur de TELEPHONE', 'Fournisseur de TELEPHONE'), ('Fournisseur de TELEVISION', 'Fournisseur de TELEVISION')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='supplier',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='supplier',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ] 