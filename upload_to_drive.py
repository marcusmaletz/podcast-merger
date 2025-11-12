#!/usr/bin/env python3
"""
Upload Datei zu Google Drive - MIT SHARED DRIVE SUPPORT
"""
import os
import sys
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def validate_folder_access(service, folder_id):
    """Prüft ob der Service Account auf den Ordner zugreifen kann"""
    try:
        print(f"🔍 Prüfe Zugriff auf Ordner: {folder_id}")
        
        # WICHTIG: supportsAllDrives=True für Shared Drives!
        folder = service.files().get(
            fileId=folder_id,
            fields='id, name, driveId',
            supportsAllDrives=True
        ).execute()
        
        folder_name = folder.get('name')
        drive_id = folder.get('driveId')
        
        print(f"✅ Ordner gefunden: {folder_name}")
        if drive_id:
            print(f"   📁 In Shared Drive: {drive_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kann nicht auf Ordner zugreifen: {e}")
        print(f"   Stelle sicher, dass:")
        print(f"   1. Die Folder-ID korrekt ist: {folder_id}")
        print(f"   2. Der Service Account Zugriff hat")
        print(f"   3. Bei Shared Drives: Service Account ist Mitglied")
        return False

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
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Drive Service erstellen
        service = build('drive', 'v3', credentials=credentials)
        
        # WICHTIG: Ordner-Zugriff validieren
        if not validate_folder_access(service, folder_id):
            return None
        
        # Dateiname aus Pfad
        file_name = os.path.basename(file_path)
        
        print(f"📤 Lade {file_name} zu Google Drive hoch...")
        
        # Datei-Metadaten
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Datei hochladen - WICHTIG: supportsAllDrives=True!
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        download_link = file.get('webContentLink')
        
        print(f"✅ Upload erfolgreich!")
        print(f"📁 File ID: {file_id}")
        print(f"🔗 View: {web_link}")
        print(f"⬇️  Download: {download_link}")
        
        # File ID für GitHub Actions speichern
        with open('drive_file_id.txt', 'w') as f:
            f.write(file_id)
        
        # Export für GitHub Actions
        github_output = os.environ.get('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a') as f:
                f.write(f"file_id={file_id}\n")
                f.write(f"file_link={web_link}\n")
                f.write(f"download_link={download_link}\n")
        
        return file_id
        
    except Exception as e:
        print(f"❌ Fehler beim Upload: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python3 upload_to_drive.py <datei> <folder_id>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    folder_id = sys.argv[2]
    
    print(f"📋 Parameter:")
    print(f"   Datei: {file_path}")
    print(f"   Ordner-ID: {folder_id}")
    
    if not os.path.exists(file_path):
        print(f"❌ Datei nicht gefunden: {file_path}")
        sys.exit(1)
    
    result = upload_to_drive(file_path, folder_id)
    sys.exit(0 if result else 1)
