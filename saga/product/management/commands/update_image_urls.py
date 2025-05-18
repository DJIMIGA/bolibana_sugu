from django.core.management.base import BaseCommand
from product.models import Product

class Command(BaseCommand):
    help = 'Met à jour les URLs des images des produits'

    def handle(self, *args, **options):
        # URLs des images pour chaque produit
        image_urls = {
            'Tecno Pop 2F Or Champagne': {
                'main': 'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-champagne/main.jpg',
                'gallery': [
                    'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-champagne/gallery/1.jpg',
                    'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-champagne/gallery/2.jpg'
                ]
            },
            'Tecno Pop 2F Noir': {
                'main': 'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-noir/main.jpg',
                'gallery': [
                    'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-noir/gallery/1.jpg',
                    'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-noir/gallery/2.jpg'
                ]
            },
            'Tecno Pop 2F Bleu': {
                'main': 'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-bleu/main.jpg',
                'gallery': [
                    'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-bleu/gallery/1.jpg',
                    'https://bolibana-sugu.s3.eu-north-1.amazonaws.com/products/tecno-pop-2f-bleu/gallery/2.jpg'
                ]
            }
        }

        # Mettre à jour les URLs des images pour chaque produit
        for title, urls in image_urls.items():
            try:
                product = Product.objects.get(title=title)
                product.image_urls = urls
                product.save()
                self.stdout.write(self.style.SUCCESS(f'URLs des images mises à jour pour {title}'))
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Produit non trouvé: {title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erreur lors de la mise à jour de {title}: {str(e)}')) 