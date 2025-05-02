from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_alter_category_options_alter_imageproduct_options_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # État de la base de données
            database_operations=[
                migrations.RunSQL(
                    """
                    DO $$
                    BEGIN
                        BEGIN
                            ALTER TABLE product_product DROP COLUMN IF EXISTS created_at CASCADE;
                        EXCEPTION
                            WHEN undefined_column THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TABLE product_product DROP COLUMN IF EXISTS updated_at CASCADE;
                        EXCEPTION
                            WHEN undefined_column THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TABLE product_product DROP COLUMN IF EXISTS is_active CASCADE;
                        EXCEPTION
                            WHEN undefined_column THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TABLE product_product DROP COLUMN IF EXISTS is_available CASCADE;
                        EXCEPTION
                            WHEN undefined_column THEN
                                NULL;
                        END;
                    END $$;
                    
                    ALTER TABLE product_product 
                        ADD COLUMN created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        ADD COLUMN updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        ADD COLUMN is_active boolean NOT NULL DEFAULT true,
                        ADD COLUMN is_available boolean NOT NULL DEFAULT false;
                    """,
                    """
                    ALTER TABLE product_product 
                        DROP COLUMN IF EXISTS created_at CASCADE,
                        DROP COLUMN IF EXISTS updated_at CASCADE,
                        DROP COLUMN IF EXISTS is_active CASCADE,
                        DROP COLUMN IF EXISTS is_available CASCADE;
                    """
                ),
            ],
            # État du modèle Django
            state_operations=[
                migrations.AddField(
                    model_name='product',
                    name='created_at',
                    field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
                ),
                migrations.AddField(
                    model_name='product',
                    name='updated_at',
                    field=models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour'),
                ),
                migrations.AddField(
                    model_name='product',
                    name='is_active',
                    field=models.BooleanField(default=True, verbose_name='Actif'),
                ),
                migrations.AddField(
                    model_name='product',
                    name='is_available',
                    field=models.BooleanField(default=False, verbose_name='Disponible en boutique'),
                ),
            ],
        ),
    ] 