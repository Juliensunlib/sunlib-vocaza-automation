import os
import csv
import paramiko
from datetime import datetime
from pyairtable import Api
from io import StringIO, BytesIO

# Configuration
BASE_ID = "appe55vTZRk6Ssd2w"
TABLE_ID = "tblcACuSWYttnFQNr"
VIEW_ID = "viwQn2IYQ5nBuXxkY"

# Field IDs
FIELD_EMAIL = "fldG47uG3mXq1qGRP"
FIELD_PRENOM = "fldhxncaPKtHlqqgZ"
FIELD_NOM = "fldfnBO2Xb6mNgAcq"
FIELD_TELEPHONE = "fldI86dLP0hkVIaMb"
FIELD_DATE_CREATION = "fldxygbu165RonF4P"
FIELD_AGENCE = "fldNY6lBfZQCXYTCa"
FIELD_STATUT_VOCAZA = "fldEAceKmwRR9we4a"
FIELD_DATE_ENVOI = "fld8QZLv3tebi4523"

# Option IDs pour Statut Vocaza
OPTION_ENVOYE = "selk5AkrlBwJ2gudt"
OPTION_ECHEC = "selqdKkqKxe5wAarj"

# SFTP Configuration
SFTP_HOST = "sunlib.enquete-en-ligne.com"
SFTP_PORT = 12360
SFTP_USERNAME = "SUNLIB-9180113"
SFTP_PASSWORD = os.environ['SFTP_PASSWORD']

print("🚀 Début de l'export Vocaza...")

# 1. Connexion Airtable
api = Api(os.environ['AIRTABLE_TOKEN'])
table = api.table(BASE_ID, TABLE_ID)

print("📊 Récupération des contacts Airtable...")

# Récupérer les records de la vue avec filtre
formula = "AND({Statut Vocaza}='', {Email}!='')"
records = table.all(view=VIEW_ID, formula=formula)

print(f"✅ {len(records)} contacts trouvés")

if len(records) == 0:
    print("ℹ️ Aucun contact à envoyer aujourd'hui")
    exit(0)

# 2. Générer le CSV
print("📝 Génération du fichier CSV...")

csv_output = StringIO()
csv_writer = csv.writer(csv_output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

# En-têtes
csv_writer.writerow(['E-mail', 'Prénom', 'Nom', 'Téléphone', 'Date_inscription', 'Agence'])

# Données
record_ids = []
for record in records:
    fields = record['fields']

    # Formatage date (ISO -> DD/MM/YYYY)
    date_inscription = ''
    if FIELD_DATE_CREATION in fields:
        date_obj = datetime.fromisoformat(fields[FIELD_DATE_CREATION].replace('Z', '+00:00'))
        date_inscription = date_obj.strftime('%d/%m/%Y')

    # Récupération agence (premier élément si liste)
    agence = ''
    if FIELD_AGENCE in fields and fields[FIELD_AGENCE]:
        agence = fields[FIELD_AGENCE][0] if isinstance(fields[FIELD_AGENCE], list) else fields[FIELD_AGENCE]

    csv_writer.writerow([
        fields.get(FIELD_EMAIL, ''),
        fields.get(FIELD_PRENOM, ''),
        fields.get(FIELD_NOM, ''),
        fields.get(FIELD_TELEPHONE, ''),
        date_inscription,
        agence
    ])

    record_ids.append(record['id'])

csv_content = csv_output.getvalue()

# Nom du fichier
timestamp = datetime.now().strftime('%Y%m%d')
filename = f"sunlib_contacts_{timestamp}.csv"

print(f"✅ CSV généré : {filename}")

# 3. Upload SFTP
print("📤 Connexion SFTP...")

try:
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    print(f"📤 Upload du fichier vers Vocaza...")

    # Upload du fichier en mode binaire avec encodage UTF-8
    csv_bytes = BytesIO(csv_content.encode('utf-8'))
    sftp.putfo(csv_bytes, f"/{filename}")

    print(f"✅ Fichier {filename} uploadé avec succès !")

    sftp.close()
    transport.close()

    upload_success = True

except Exception as e:
    print(f"❌ Erreur SFTP : {str(e)}")
    upload_success = False

# 4. Mise à jour Airtable
print("🔄 Mise à jour des statuts Airtable...")

today = datetime.now().strftime('%Y-%m-%d')

for record_id in record_ids:
    try:
        if upload_success:
            # Succès : Statut "Envoyé" + Date d'envoi
            table.update(record_id, {
                FIELD_STATUT_VOCAZA: OPTION_ENVOYE,
                FIELD_DATE_ENVOI: today
            })
        else:
            # Échec : Statut "Echec"
            table.update(record_id, {
                FIELD_STATUT_VOCAZA: OPTION_ECHEC
            })
    except Exception as e:
        print(f"⚠️ Erreur mise à jour record {record_id}: {str(e)}")

print("✅ Mise à jour Airtable terminée")

# 5. Résumé
print("\n" + "="*50)
print("📊 RÉSUMÉ DE L'EXPORT")
print("="*50)
print(f"Contacts exportés : {len(records)}")
print(f"Fichier : {filename}")
print(f"Statut upload : {'✅ Succès' if upload_success else '❌ Échec'}")
print(f"Heure : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*50)
