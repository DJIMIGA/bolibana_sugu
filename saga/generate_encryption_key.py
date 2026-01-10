"""
Script pour générer une clé de chiffrement pour les clés API
"""
from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    print("\n" + "="*60)
    print("CLÉ DE CHIFFREMENT GÉNÉRÉE")
    print("="*60)
    print(f"\n{key.decode()}\n")
    print("="*60)
    print("\nAjoutez cette clé dans votre fichier .env :")
    print(f"INVENTORY_ENCRYPTION_KEY={key.decode()}\n")
    print("="*60 + "\n")

