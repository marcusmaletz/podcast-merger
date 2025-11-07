#!/usr/bin/env python3
"""
Podcast MP3 Merger - Einfache Version mit FFmpeg
Funktioniert ohne pydub!
"""

import os
import sys
import subprocess

def merge_podcast_files(intro_path, main_path, outro_path, output_path):
    """
    Fügt Intro, Hauptteil und Outro zu einer finalen MP3-Datei zusammen
    Verwendet FFmpeg direkt (keine Python-Bibliotheken nötig!)
    """
    try:
        # Prüfe ob FFmpeg installiert ist
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ FFmpeg ist nicht installiert!")
            print("   Installiere es mit: brew install ffmpeg")
            return False
        
        print("🎙️  Lade Audio-Dateien...")
        
        # Erstelle temporäre Dateiliste für FFmpeg
        filelist_path = 'temp_filelist.txt'
        with open(filelist_path, 'w') as f:
            f.write(f"file '{os.path.abspath(intro_path)}'\n")
            f.write(f"file '{os.path.abspath(main_path)}'\n")
            f.write(f"file '{os.path.abspath(outro_path)}'\n")
        
        print(f"   ✓ Intro: {intro_path}")
        print(f"   ✓ Hauptteil: {main_path}")
        print(f"   ✓ Outro: {outro_path}")
        
        # Füge Dateien mit FFmpeg zusammen
        print("\n🔧 Füge Dateien zusammen...")
        print("   (Dies kann einen Moment dauern...)")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', filelist_path,
            '-c:a', 'libmp3lame',  # Re-encode mit MP3
            '-b:a', '192k',        # Bitrate 192 kbps
            '-ar', '44100',        # Sample Rate 44.1 kHz
            '-y',                  # Überschreibe Ausgabedatei falls vorhanden
            output_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Lösche temporäre Dateiliste
        if os.path.exists(filelist_path):
            os.remove(filelist_path)
        
        if result.returncode == 0:
            # Prüfe ob Ausgabedatei existiert
            if os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"\n💾 Gespeichert: {output_path}")
                print(f"   Größe: {size_mb:.2f} MB")
                print("\n✅ Fertig! Podcast erfolgreich erstellt.")
                return True
            else:
                print(f"❌ Fehler: Ausgabedatei wurde nicht erstellt")
                return False
        else:
            print(f"❌ FFmpeg Fehler:")
            print(result.stderr)
            return False
        
    except FileNotFoundError as e:
        print(f"❌ Fehler: Datei nicht gefunden - {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Verarbeiten: {e}")
        return False


def main():
    """Hauptfunktion mit Kommandozeilen-Interface"""
    
    if len(sys.argv) != 5:
        print("📖 Verwendung:")
        print(f"   python3 {sys.argv[0]} <intro.mp3> <hauptteil.mp3> <outro.mp3> <output.mp3>")
        print("\nBeispiel:")
        print(f"   python3 {sys.argv[0]} intro.mp3 mein_podcast.mp3 outro.mp3 fertig.mp3")
        sys.exit(1)
    
    intro_path = sys.argv[1]
    main_path = sys.argv[2]
    outro_path = sys.argv[3]
    output_path = sys.argv[4]
    
    # Prüfe ob Dateien existieren
    for path, name in [(intro_path, "Intro"), (main_path, "Hauptteil"), (outro_path, "Outro")]:
        if not os.path.exists(path):
            print(f"❌ Fehler: {name}-Datei nicht gefunden: {path}")
            sys.exit(1)
    
    # Führe Zusammenführung durch
    success = merge_podcast_files(intro_path, main_path, outro_path, output_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
