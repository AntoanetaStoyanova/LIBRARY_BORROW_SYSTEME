## Exo 1: une API base de données

Construire une API pour une base de données simple d'une bibliothèque avec SQLAlchemy.
La base de données :
- 2 entités :
    - lecteur : nom, prénom, mail, password
    - livres : titre, auteur, isbn
- un lecteur peut emprunter un livre avec une date d'emprunt et une date de retour
- un lecteur peut consulter ses emprunts en cours et passés
- un lecteur peut consulter si un livre est disponible (pour simplifier on considère qu'il n'y a qu'un seul exemplaire de chaque livre)

**Contraintes :**
- Intégrer toutes les requêtes CRUD nécessaires.
- Gérer les schémas de récupération des données du client et les schémas de réponse au client.
- Intégrer l'authentification pour permettre à un lecteur authentifié de consulter ses emprunts



