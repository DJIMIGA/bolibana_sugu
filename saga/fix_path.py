import os
import sys
from pathlib import Path

def fix_pythonpath():
    """Corrige le PYTHONPATH pour le projet Django."""
    print("\n=== Correction du PYTHONPATH ===")
    
    # Obtenir le chemin absolu du projet
    BASE_DIR = Path(__file__).resolve().parent.parent
    print(f"\nRépertoire de base du projet : {BASE_DIR}")
    
    # Chemins à ajouter
    paths_to_add = [
        str(BASE_DIR),
        str(BASE_DIR / 'saga'),
        str(BASE_DIR / 'saga' / 'product'),
        str(BASE_DIR / 'saga' / 'accounts'),
        str(BASE_DIR / 'saga' / 'suppliers'),
        str(BASE_DIR / 'saga' / 'cart'),
        str(BASE_DIR / 'saga' / 'price_checker'),
    ]
    
    # Nettoyer le PYTHONPATH actuel
    current_paths = set(sys.path)
    new_paths = []
    
    # Ajouter les nouveaux chemins
    for path in paths_to_add:
        if path not in current_paths:
            new_paths.append(path)
    
    # Ajouter les chemins existants qui ne sont pas dans les nouveaux chemins
    for path in current_paths:
        if path not in paths_to_add and os.path.exists(path):
            new_paths.append(path)
    
    # Mettre à jour sys.path
    sys.path = new_paths
    
    # Vérifier et afficher les chemins
    print("\nChemins valides dans PYTHONPATH :")
    for path in sys.path:
        if os.path.exists(path):
            print(f"✓ {path}")
        else:
            print(f"✗ {path} (n'existe pas)")
    
    print("\n=== Fin de la correction du PYTHONPATH ===\n")
    
    return sys.path

if __name__ == '__main__':
    fix_pythonpath() 