import os
import requests
import subprocess
import time

def download_file(url, filename):
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(1024): f.write(chunk)
            return True
    except: pass
    return False

def assemble_video(assets, output_filename, music_url=None):
    if not assets: return

    video_clips = []
    assets = sorted(assets, key=lambda x: x['id'])
    
    print("🎬 Assemblage Final...")

    # ÉTAPE 1 : Création des clips individuels
    for asset in assets:
        seg_id = asset['id']
        rv = f"temp_v_{seg_id}.mp4"
        ra = f"temp_a_{seg_id}.mp3"
        rs = f"temp_s_{seg_id}.srt" 
        merged = f"clip_{seg_id}.mp4"
        
        has_video = download_file(asset['video_url'], rv)
        has_audio = download_file(asset['audio_url'], ra)
        
        has_subs = False
        if asset.get('srt_content'):
            # --- FIX SRT : Encodage UTF-8 simple ---
            try:
                with open(rs, "w", encoding="utf-8") as f:
                    f.write(asset['srt_content'])
                has_subs = True
            except Exception as e:
                print(f"   ⚠️ Erreur écriture SRT {seg_id}: {e}")

        if has_video and has_audio:
            try:
                # 1. Scale/Crop
                filter_complex = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30[vbase];"
                
                # 2. Incrustation Sous-titres
                if has_subs:
                    # Astuce ultime Windows : on remplace tous les backslashes par des slashs
                    # et on échappe le ':' du disque (C:/) si on était en absolu.
                    # Ici on est en relatif, donc juste le nom du fichier suffit généralement.
                    rs_clean = rs.replace("\\", "/")
                    
                    # Style Jaune
                    style = "Fontname=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=50"
                    
                    filter_complex += f"[vbase]subtitles='{rs_clean}':force_style='{style}'[vout]"
                else:
                    filter_complex += "[vbase]copy[vout]"

                cmd = [
                    'ffmpeg', '-y', '-v', 'error',
                    '-i', rv, 
                    '-i', ra, 
                    '-filter_complex', filter_complex,
                    '-map', '[vout]', 
                    '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'fast',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-af', 'apad', 
                    '-shortest', 
                    merged
                ]
                subprocess.run(cmd, check=True)
                video_clips.append(merged)
                print(f"   ✅ Clip {seg_id} prêt (Subs: {has_subs}).")
            except Exception as e:
                print(f"   ❌ Erreur clip {seg_id}: {e}")
        
        # Cleanup
        if os.path.exists(rv): os.remove(rv)
        if os.path.exists(ra): os.remove(ra)
        if os.path.exists(rs): os.remove(rs)

    if not video_clips: return

    # ÉTAPE 2 : Concaténation
    concat_file = f"temp_concat_{int(time.time())}.mp4"
    list_file = f"concat_list_{int(time.time())}.txt"
    
    with open(list_file, "w") as f:
        for clip in video_clips:
            f.write(f"file '{os.path.abspath(clip).replace(os.sep, '/')}'\n")
            
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error',
        '-f', 'concat', '-safe', '0', '-i', list_file, 
        '-c', 'copy', concat_file
    ], check=True)

    # ÉTAPE 3 : Mixage Musique
    final_output = concat_file # Par défaut
    
    if music_url:
        rm = f"temp_music_{int(time.time())}.mp3"
        if download_file(music_url, rm):
            print("   🎵 Mixage musique de fond...")
            try:
                cmd_mix = [
                    'ffmpeg', '-y', '-v', 'error',
                    '-i', concat_file,
                    '-i', rm,
                    # Volume musique 15% + Mixage + Cut à la fin de la vidéo
                    '-filter_complex', "[1:a]volume=0.15[m];[0:a][m]amix=inputs=2:duration=first[aout]",
                    '-map', '0:v',
                    '-map', '[aout]',
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    output_filename
                ]
                subprocess.run(cmd_mix, check=True)
                final_output = output_filename # Succès
                
                if os.path.exists(rm): os.remove(rm)
                if os.path.exists(concat_file): os.remove(concat_file)
            except Exception as e:
                print(f"   ❌ Erreur mixage musique: {e}")
                # Fallback : on garde la vidéo sans musique mais renommée
                if os.path.exists(concat_file): os.rename(concat_file, output_filename)
        else:
            if os.path.exists(concat_file): os.rename(concat_file, output_filename)
    else:
        if os.path.exists(concat_file): os.rename(concat_file, output_filename)

    # Nettoyage final
    for clip in video_clips: 
        if os.path.exists(clip): os.remove(clip)
    if os.path.exists(list_file): os.remove(list_file)
    
    print(f"✨ VIDÉO FINALE PRÊTE : {output_filename}")