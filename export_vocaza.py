import os
import csv
import paramiko
from datetime import datetime
from pyairtable import Api

BASE_ID = "appe55vTZRk6Ssd2w"
TABLE_ID = "tblcACuSWYttnFQNr"
VIEW_ID = "viwQn2IYQ5nBuXxkY"

# Noms de champs (plus robustes que les IDs)
COL_PDL = "N° de PDL"
COL_NOM = "Nom"
COL_PRENOM = "Prenom"
COL_NOM_ENTREPRISE = "Nom de l'entreprise"
COL_CIVILITE = "Civilité Abonné 1"
COL_EMAIL = "Email"
COL_INSTALLATEUR = "Nom de l'entreprise (from Installateur )"
COL_CONFIG_CLIENT = "Champs IA Config client"
COL_STATUT_VOCAZA = "Statut Vocaza"
COL_DATE_ENVOI = "Date d'envoi Vocaza"

SFTP_HOST = "sunlib.enquete-en-ligne.com"
SFTP_PORT = 12360
SFTP_USERNAME = "SUNLIB-9180113"
SFTP_PASSWORD = os.environ['SFTP_PASSWORD']

def get_field_value(fields, field_name, default=''):
    value = fields.get(field_name, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value if value else default

print("🚀 Début de l'export Vocaza...")

api = Api(os.environ['AIRTABLE_TOKEN'])
table = api.table(BASE_ID, TABLE_ID)

print("📊 Récupération des contacts Airtable...")
formula = f"AND({{{COL_STATUT_VOCAZA}}}='', {{{COL_EMAIL}}}!='')"
records = table.all(view=VIEW_ID, formula=formula)
print(f"✅ {len(records)} contacts trouvés")

if len(records) == 0:
    print("ℹ️ Aucun contact à envoyer aujourd'hui")
    exit(0)

# Génération CSV
timestamp = datetime.now().strftime('%Y%m%d')
filename = f"sunlib_contacts_{timestamp}.csv"
temp_file = f"/tmp/{filename}"

record_ids = []

with open(temp_file, 'w', encoding='cp1252', errors='replace', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        'N° de PDL', 'Nom', 'Prenom', "Nom de l'entreprise",
        'Civilité Abonné 1', 'Email', 'Installateur', 'Champs IA Config client'
    ])
    for record in records:
        fields = record['fields']
        writer.writerow([
            get_field_value(fields, COL_PDL),
            get_field_value(fields, COL_NOM),
            get_field_value(fields, COL_PRENOM),
            get_field_value(fields, COL_NOM_ENTREPRISE),
            get_field_value(fields, COL_CIVILITE),
            get_field_value(fields, COL_EMAIL),
            get_field_value(fields, COL_INSTALLATEUR),
            get_field_value(fields, COL_CONFIG_CLIENT)
        ])
        record_ids.append(record['id'])

print(f"✅ CSV généré : {filename}")

# Upload SFTP
print("📤 Connexion SFTP...")
upload_success = False
try:
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    with open(temp_file, 'rb') as f:
        sftp.putfo(f, f"/{filename}")
    sftp.close()
    transport.close()
    upload_success = True
    print(f"✅ Fichier uploadé avec succès !")
except Exception as e:
    print(f"❌ Erreur SFTP : {str(e)}")

# Mise à jour Airtable
print("🔄 Mise à jour des statuts Airtable...")
today = datetime.now().strftime('%Y-%m-%d')

for record_id in record_ids:
    try:
        if upload_success:
            table.update(record_id, {
                COL_STATUT_VOCAZA: "Envoyé",
                COL_DATE_ENVOI: today
            })
        else:
            table.update(record_id, {COL_STATUT_VOCAZA: "Échec"})
    except Exception as e:
        print(f"⚠️ Erreur mise à jour record {record_id}: {str(e)}")

print(f"\n{'='*50}")
print(f"Contacts exportés : {len(records)}")
print(f"Statut : {'✅ Succès' if upload_success else '❌ Échec'}")
print(f"{'='*50}")
