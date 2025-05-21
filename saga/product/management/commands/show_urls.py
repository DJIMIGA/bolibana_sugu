from django.core.management.base import BaseCommand
from django.urls import get_resolver

class Command(BaseCommand):
    help = 'Affiche toutes les URLs de l\'application'

    def handle(self, *args, **options):
        resolver = get_resolver()
        urls = []
        
        def extract_urls(urlpatterns, base=''):
            for pattern in urlpatterns:
                if hasattr(pattern, 'url_patterns'):
                    extract_urls(pattern.url_patterns, base + pattern.pattern.regex.pattern)
                else:
                    urls.append({
                        'url': base + pattern.pattern.regex.pattern,
                        'name': pattern.name,
                        'callback': pattern.callback.__name__ if hasattr(pattern, 'callback') else 'N/A'
                    })

        extract_urls(resolver.url_patterns)
        
        self.stdout.write(self.style.SUCCESS('\nListe des URLs :\n'))
        for url in sorted(urls, key=lambda x: x['url']):
            self.stdout.write(f"URL: {url['url']}")
            self.stdout.write(f"Nom: {url['name']}")
            self.stdout.write(f"Callback: {url['callback']}")
            self.stdout.write('-' * 50) 