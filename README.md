# Sunlib Vocaza Automation

Script d'export automatique des contacts Airtable vers Vocaza via SFTP.

## Fonctionnalités

- Récupération quotidienne des nouveaux contacts depuis Airtable
- Génération d'un fichier CSV formaté pour Vocaza
- Upload automatique via SFTP
- Mise à jour des statuts dans Airtable

## Configuration

### Variables d'environnement requises

Créez un fichier `.env` avec :

```
AIRTABLE_TOKEN=votre_token_airtable
SFTP_PASSWORD=votre_mot_de_passe_sftp
```

### GitHub Secrets

Pour l'exécution automatique via GitHub Actions, configurez ces secrets :

- `AIRTABLE_TOKEN`
- `SFTP_PASSWORD`

## Installation locale

```bash
pip install -r requirements.txt
python export_vocaza.py
```

## Exécution automatique

Le workflow GitHub Actions s'exécute automatiquement tous les jours à 17h UTC (18h Paris).

Vous pouvez aussi le déclencher manuellement depuis l'onglet "Actions" de GitHub.

## Format du fichier CSV

Le fichier généré contient les colonnes suivantes (format requis par Vocaza) :

- N° de PDL (vide)
- Nom
- Prenom (sans accent)
- Nom de l'entreprise (vide)
- Civilité Abonné 1 (vide)
- Email (avec majuscule)
- Installateur (agence depuis Airtable)
- Champs IA Config client (valeur par défaut: "Duo")