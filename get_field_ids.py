import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

BASE_ID = "appe55vTZRk6Ssd2w"
TABLE_ID = "tblcACuSWYttnFQNr"

api = Api(os.environ['AIRTABLE_TOKEN'])
table = api.table(BASE_ID, TABLE_ID)

print("📋 Récupération des champs de la table Airtable...\n")

# Récupérer le schéma de la table
schema = api.base(BASE_ID).schema()
table_schema = next((t for t in schema.tables if t.id == TABLE_ID), None)

if table_schema:
    print(f"Table: {table_schema.name}\n")
    print("Champs trouvés:")
    print("-" * 80)

    for field in table_schema.fields:
        print(f"Nom: {field.name:40} | ID: {field.id}")

    print("-" * 80)
    print("\n✅ Recherche des champs Vocaza:")

    vocaza_fields = [
        "N° de PDL",
        "Nom",
        "Prenom",
        "Nom de l'entreprise",
        "Civilité Abonné 1",
        "Email",
        "Installateur",
        "Champs IA Config client"
    ]

    for field_name in vocaza_fields:
        field = next((f for f in table_schema.fields if f.name == field_name), None)
        if field:
            print(f"✓ {field_name:30} → {field.id}")
        else:
            print(f"✗ {field_name:30} → NON TROUVÉ")
else:
    print("❌ Table non trouvée")
