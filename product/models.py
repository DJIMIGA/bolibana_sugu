class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Prix')
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    highlight = models.TextField(verbose_name='Points forts', blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disponible_salam = models.BooleanField(default=False, verbose_name='Disponible en Salam')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU', default='SKU-0000')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='products', null=True, blank=True)

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']
        unique_together = [['title', 'category']]

    def __str__(self):
        return self.title

    def clean(self):
        if Product.objects.filter(title=self.title, category=self.category).exclude(pk=self.pk).exists():
            raise ValidationError(
                {'title': 'Un produit avec ce titre existe déjà dans cette catégorie.'}
            )

    def save(self, *args, **kwargs):
        self.title = self.title.strip().title()
        if self.description:
            self.description = self.description.strip()
        if self.highlight:
            self.highlight = self.highlight.strip()
        if self.image and hasattr(self.image, 'file'):
            optimizer = ImageOptimizer()
            if optimizer.validate_image(self.image.file):
                self.image.file = optimizer.optimize_image(self.image.file)
        super().save(*args, **kwargs)

    def get_highlights(self):
        if self.highlight:
            return self.highlight.splitlines() 