from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings
from django.contrib import admin

class Command(BaseCommand):
    help = 'Affiche toutes les URLs de l\'application avec une section spéciale pour les URLs admin'

    def handle(self, *args, **options):
        resolver = get_resolver()
        urls = []
        admin_urls = []
        
        def extract_urls(urlpatterns, base=''):
            for pattern in urlpatterns:
                if hasattr(pattern, 'url_patterns'):
                    extract_urls(pattern.url_patterns, base + pattern.pattern.regex.pattern)
                else:
                    url_info = {
                        'url': base + pattern.pattern.regex.pattern,
                        'name': pattern.name,
                        'callback': pattern.callback.__name__ if hasattr(pattern, 'callback') else 'N/A'
                    }
                    
                    # Vérifier si c'est une URL admin
                    if 'admin' in url_info['url'] or 'admin' in str(url_info['callback']):
                        admin_urls.append(url_info)
                    else:
                        urls.append(url_info)

        extract_urls(resolver.url_patterns)
        
        # Afficher la configuration admin
        self.stdout.write(self.style.SUCCESS('\n=== Configuration Admin ==='))
        self.stdout.write(f"URL Admin configurée : {getattr(settings, 'ADMIN_URL', 'admin/')}")
        self.stdout.write(f"URL Admin réelle : {admin.site.site_url}")
        self.stdout.write('=' * 50)
        
        # Afficher les URLs admin
        self.stdout.write(self.style.SUCCESS('\n=== URLs Admin ==='))
        for url in sorted(admin_urls, key=lambda x: x['url']):
            self.stdout.write(self.style.WARNING(f"URL: {url['url']}"))
            self.stdout.write(f"Nom: {url['name']}")
            self.stdout.write(f"Callback: {url['callback']}")
            self.stdout.write('-' * 50)
        
        # Afficher les autres URLs
        self.stdout.write(self.style.SUCCESS('\n=== Autres URLs ==='))
        for url in sorted(urls, key=lambda x: x['url']):
            self.stdout.write(f"URL: {url['url']}")
            self.stdout.write(f"Nom: {url['name']}")
            self.stdout.write(f"Callback: {url['callback']}")
            self.stdout.write('-' * 50) 