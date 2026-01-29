#!/usr/bin/env python3
"""
Script de test pour vérifier l'encodage UTF-8 avec SFTP
"""
import os
from io import StringIO, BytesIO

# Créer un contenu CSV avec des caractères accentués
csv_content = "E-mail;Prénom;Nom;Téléphone;Date_inscription;Agence\n"
csv_content += "test@example.com;François;Dupré;0601020304;29/01/2026;Agence Paris\n"

print("📝 Contenu CSV généré:")
print(csv_content)
print(f"\n📏 Taille en string: {len(csv_content)} caractères")

# Test avec StringIO (ancienne méthode - problématique)
string_io = StringIO(csv_content)
string_bytes = string_io.getvalue().encode('utf-8')
print(f"📦 Taille StringIO encodé: {len(string_bytes)} octets")

# Test avec BytesIO (nouvelle méthode - correcte)
byte_io = BytesIO(csv_content.encode('utf-8'))
byte_content = byte_io.getvalue()
print(f"✅ Taille BytesIO: {len(byte_content)} octets")

print("\n✨ L'encodage est correct si les deux tailles BytesIO sont identiques")
