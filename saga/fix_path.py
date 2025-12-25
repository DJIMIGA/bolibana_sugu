import os
import sys
from pathlib import Path

def fix_pythonpath():
    """Corrige le PYTHONPATH pour le projet Django."""
    print("\n=== Correction du PYTHONPATH ===")
    
    # Obtenir le chemin absolu du projet
    BASE_DIR = Path(__file__).resolve().parent.parent
    print(f"\nRépertoire de base du projet : {BASE_DIR}")
    
    # Chemins du projet à ajouter
    project_paths = [
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
    
    # Ajouter les chemins du projet en premier
    for path in project_paths:
        if path not in current_paths:
            new_paths.append(path)
    
    # Ajouter les chemins de l'environnement virtuel et les chemins système essentiels
    for path in current_paths:
        # Inclure TOUS les chemins de l'environnement virtuel (priorité absolue)
        if '.env' in path or 'venv' in path or 'virtualenv' in path:
            new_paths.append(path)
        # Inclure les chemins système essentiels (mais pas Python 3.9)
        elif 'site-packages' in path and 'Python39' not in path:
            new_paths.append(path)
        # Inclure les chemins DLLs essentiels (mais pas Python 3.9)
        elif 'DLLs' in path and 'Python39' not in path:
            new_paths.append(path)
        # Inclure les chemins lib essentiels (mais pas Python 3.9)
        elif 'lib' in path and 'Python39' not in path and os.path.exists(path):
            new_paths.append(path)
        # Inclure les autres chemins existants (mais pas Python 3.9)
        elif os.path.exists(path) and 'Python39' not in path:
            new_paths.append(path)
    
    # Mettre à jour sys.path
    sys.path = new_paths
    
    # Vérifier et afficher les chemins
    print("\nChemins valides dans PYTHONPATH :")
    for path in sys.path:
        if os.path.exists(path):
            print(f"[OK] {path}")
        else:
            print(f"[ERROR] {path} (n'existe pas)")
    
    print("\n=== Fin de la correction du PYTHONPATH ===\n")
    
    return sys.path

if __name__ == '__main__':
    fix_pythonpath() 