#!/usr/bin/env python3
"""
Upload Datei zu Google Drive
Verwendet Service Account für GitHub Actions
"""

import os
import sys
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path, folder_id):
    """
    Lädt eine Datei zu Google Drive hoch
    
    Args:
        file_path: Pfad zur hochzuladenden Datei
        folder_id: Google Drive Ordner-ID
    """
    try:
        # Credentials aus Environment Variable
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            print("❌ GOOGLE_CREDENTIALS nicht gesetzt!")
            return None
        
        # Parse Credentials
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Drive Service erstellen
        service = build('drive', 'v3', credentials=credentials)
        
        # Dateiname aus Pfad
        file_name = os.path.basename(file_path)
        
        # Datei-Metadaten
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Datei hochladen
        media = MediaFileUpload(file_path, resumable=True)
        
        print(f"📤 Lade {file_name} zu Google Drive hoch...")
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        
        print(f"✅ Erfolgreich hochgeladen!")
        print(f"   File ID: {file_id}")
        print(f"   Link: {web_link}")
        
        # Export FILE_ID für GitHub Actions
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write(f"file_id={file_id}\n")
            f.write(f"file_link={web_link}\n")
        
        return file_id
        
    except Exception as e:
        print(f"❌ Fehler beim Upload: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python3 upload_to_drive.py <datei> <folder_id>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    folder_id = sys.argv[2]
    
    if not os.path.exists(file_path):
        print(f"❌ Datei nicht gefunden: {file_path}")
        sys.exit(1)
    
    result = upload_to_drive(file_path, folder_id)
    sys.exit(0 if result else 1)

# Am Ende von upload_to_drive.py, nach dem Upload:

file_id = file.get('id')
print(f"✅ Upload erfolgreich!")
print(f"📁 File ID: {file_id}")
print(f"🔗 View: {file.get('webViewLink')}")

# File ID für GitHub Actions speichern
with open('drive_file_id.txt', 'w') as f:
    f.write(file_id)
