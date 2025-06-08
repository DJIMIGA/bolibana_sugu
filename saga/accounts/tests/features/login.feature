Feature: Authentification avec 2FA
  En tant qu'utilisateur
  Je veux me connecter de manière sécurisée
  Afin de protéger mon compte

  Scenario: Connexion réussie avec 2FA
    Given un utilisateur avec email "test@example.com" et mot de passe "testpassword123"
    When je me connecte avec email "test@example.com" et mot de passe "testpassword123"
    Then je suis redirigé vers la page de vérification 2FA
    When j'entre le code de vérification "123456"
    Then je suis connecté et redirigé vers la page d'accueil

  Scenario: Code 2FA expiré
    Given un utilisateur avec email "test@example.com" et mot de passe "testpassword123"
    And le code 2FA a expiré
    When je me connecte avec email "test@example.com" et mot de passe "testpassword123"
    Then je suis redirigé vers la page de vérification 2FA
    When j'entre le code de vérification "123456"
    Then je vois un message d'erreur "Code expiré"

  Scenario: Code 2FA invalide
    Given un utilisateur avec email "test@example.com" et mot de passe "testpassword123"
    When je me connecte avec email "test@example.com" et mot de passe "testpassword123"
    Then je suis redirigé vers la page de vérification 2FA
    When j'entre le code de vérification "000000"
    Then je vois un message d'erreur "Code invalide"

  Scenario: Identifiants invalides
    Given un utilisateur avec email "test@example.com" et mot de passe "testpassword123"
    When je me connecte avec email "test@example.com" et mot de passe "wrongpassword"
    Then je vois un message d'erreur "Identifiants invalides" 