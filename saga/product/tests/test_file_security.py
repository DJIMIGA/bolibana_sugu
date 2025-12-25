from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from product.models import Category
from django.contrib.contenttypes.models import ContentType
import io
from PIL import Image

class FileSecurityTest(TestCase):
    def test_upload_malicious_file_fails(self):
        """Vérifie qu'un fichier malveillant (ex: script déguisé en image) est rejeté."""
        # Création d'un faux fichier image qui contient en fait du texte/script
        malicious_content = b"<?php echo 'Hacked'; ?>"
        fake_image = SimpleUploadedFile(
            "test.png", 
            malicious_content, 
            content_type="image/png"
        )
        
        # Obtenir un ContentType pour la catégorie
        content_type = ContentType.objects.get_for_model(Category)
        
        category = Category(
            name="Test Cat",
            image=fake_image,
            category_type='MODEL',
            content_type=content_type
        )
        
        # La validation devrait échouer à cause du validateur validate_image_file
        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_upload_valid_image_passes(self):
        """Vérifie qu'une vraie image passe la validation."""
        # Création d'une vraie image PNG en mémoire
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        
        valid_image = SimpleUploadedFile(
            "test.png",
            file.read(),
            content_type="image/png"
        )
        
        # Obtenir un ContentType
        content_type = ContentType.objects.get_for_model(Category)
        
        category = Category(
            name="Valid Cat",
            image=valid_image,
            category_type='MODEL',
            content_type=content_type
        )
        
        # Ne devrait pas lever d'exception
        try:
            category.full_clean()
        except ValidationError as e:
            self.fail(f"La validation a échoué pour une image valide : {e}")

