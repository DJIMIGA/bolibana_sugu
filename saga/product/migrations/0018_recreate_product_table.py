from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_reset_product_fields'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                -- Supprimer toutes les contraintes de clé étrangère
                EXECUTE (
                    SELECT string_agg('ALTER TABLE ' || quote_ident(conrelid::regclass::text) || 
                                    ' DROP CONSTRAINT ' || quote_ident(conname), '; ')
                    FROM pg_constraint
                    WHERE confrelid = 'product_product'::regclass::oid
                );

                -- Supprimer la table
                DROP TABLE IF EXISTS product_product CASCADE;

                -- Recréer la table
                CREATE TABLE product_product (
                    id bigserial PRIMARY KEY,
                    name varchar(255) NOT NULL,
                    description text,
                    price numeric(10,2) NOT NULL,
                    stock integer NOT NULL,
                    sku varchar(100) NOT NULL UNIQUE,
                    category_id bigint NOT NULL,
                    supplier_id bigint NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_active boolean NOT NULL DEFAULT true,
                    is_available boolean NOT NULL DEFAULT false,
                    image varchar(100)
                );

                -- Recréer les contraintes de clé étrangère
                ALTER TABLE product_product 
                    ADD CONSTRAINT product_product_category_id_fkey 
                    FOREIGN KEY (category_id) REFERENCES product_category(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE product_product 
                    ADD CONSTRAINT product_product_supplier_id_fkey 
                    FOREIGN KEY (supplier_id) REFERENCES product_supplier(id) DEFERRABLE INITIALLY DEFERRED;
            END $$;
            """,
            """
            SELECT 1;
            """
        ),
    ] 