import os
import asyncio
import fal_client
import random
from dotenv import load_dotenv

load_dotenv()

NEGATIVE_PROMPT = "nsfw, nude, gore, violence, deformed, bad anatomy, text, watermark, low quality, static, motionless, ugly, distorted hands, extra limbs, morphing, changing clothes, aging, blurry background, letterbox, letterboxing, black bars, cinematic bars, pillarbox, wide screen frame."

def json_to_srt(json_data):
    """
    Convertit le résultat de Wizper (JSON) en format SRT standard.
    Gère les formats 'segments' (OpenAI) et 'chunks' (Fal/Wizper).
    """
    srt_content = ""
    
    if not json_data: return ""
    
    # 1. Tentative format standard 'segments'
    segments = json_data.get('segments')

    # 2. Tentative format 'chunks' (Celui qui posait problème)
    if not segments and 'chunks' in json_data:
        segments = []
        for chunk in json_data['chunks']:
            # Les chunks ont souvent le format: {'text': '...', 'timestamp': [start, end]}
            text = chunk.get('text', '')
            timestamp = chunk.get('timestamp')
            if isinstance(timestamp, (list, tuple)) and len(timestamp) >= 2:
                segments.append({
                    'start': timestamp[0],
                    'end': timestamp[1],
                    'text': text
                })
    
    if not segments:
        # Debug pour comprendre si l'API change encore
        print(f"      ⚠️ Wizper: Pas de segments/chunks trouvés. Keys: {list(json_data.keys())}")
        return ""
    
    for i, seg in enumerate(segments):
        # Sécurisation des types (float)
        try:
            start = float(seg.get('start', 0))
            end = float(seg.get('end', 0))
            text = seg.get('text', '').strip()
        except ValueError:
            continue
        
        def format_time(seconds):
            millis = int((seconds % 1) * 1000)
            seconds = int(seconds)
            mins, secs = divmod(seconds, 60)
            hours, mins = divmod(mins, 60)
            return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"
            
        srt_content += f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n"
    
    return srt_content

async def generate_music_track(prompt, duration=30):
    """Génère une musique de fond avec AceStep (Compatible V2)."""
    print(f"🎵 Génération Musique (AceStep): {prompt} ({duration}s)")
    try:
        tag_list = [word for word in prompt.replace(',', '').split() if len(word) > 3][:3]
        if not tag_list: tag_list = ["cinematic", "background"]
        tags_str = ", ".join(tag_list)

        res = await asyncio.to_thread(fal_client.subscribe,
            "fal-ai/ace-step",
            arguments={
                "prompt": prompt,
                "seconds_total": duration,
                "tags": tags_str
            }
        )
        
        # --- FIX MUSIQUE : Gestion de toutes les structures de réponse possibles ---
        url = None
        if 'audio' in res:
            if isinstance(res['audio'], dict) and 'url' in res['audio']:
                url = res['audio']['url']
            elif isinstance(res['audio'], str):
                url = res['audio']
        elif 'audio_url' in res:
             if isinstance(res['audio_url'], dict) and 'url' in res['audio_url']:
                url = res['audio_url']['url']
             else:
                url = res['audio_url']
        elif 'file_url' in res:
            url = res['file_url']

        if url:
            print("   ✅ Musique générée")
            return url
        else:
            print(f"   ⚠️ Réponse AceStep non reconnue: {res.keys()}")
            return None

    except Exception as e:
        print(f"   ❌ Erreur Musique: {e}")
        return None

async def generate_storyboard_async(plan, indices=None):
    """Génère les images de référence (Flux Schnell) AVEC SEED."""
    loop = asyncio.get_event_loop()
    tasks = []
    
    project_seed = plan.get('consistency_seed', 424242)
    target_indices = [str(x) for x in indices] if indices else None
    
    print(f"📸 DÉBUT Storyboard (Flux) - SEED: {project_seed}")
    
    def call_fal_image(prompt, seg_id, seed):
        print(f"   ➤ [Img {seg_id}] Envoi (Seed: {seed})...")
        try:
            clean_prompt = prompt.strip()
            res = fal_client.subscribe(
                "fal-ai/flux/schnell", 
                arguments={
                    "prompt": f"{clean_prompt}, vertical portrait 9:16 aspect ratio, sharp focus, high detail, full screen coverage.", 
                    "image_size": "portrait_16_9",
                    "num_inference_steps": 4,
                    "seed": seed
                }
            )
            print(f"   ✅ [Img {seg_id}] OK")
            return {"id": seg_id, "url": res['images'][0]['url']}
        except Exception as e:
            print(f"   ❌ [Img {seg_id}] Erreur: {e}")
            return {"id": seg_id, "error": str(e)}

    for seg in plan['segments']:
        seg_id_str = str(seg['segment_id'])
        current_seed = project_seed
        if target_indices is not None:
            if seg_id_str in target_indices:
                current_seed = random.randint(100000, 999999) 
            else:
                continue
        
        prompt = seg.get('visual_prompt', seg.get('visual_description', ''))
        tasks.append(loop.run_in_executor(None, call_fal_image, prompt, seg['segment_id'], current_seed))
    
    results = await asyncio.gather(*tasks)
    images = {}
    for res in results:
        if "url" in res: images[res["id"]] = res["url"]
    return images

async def produce_short_async(plan, image_map=None):
    """Pipeline PRO : Audio + Vidéo + Sous-titres (Wizper)"""
    loop = asyncio.get_event_loop()
    
    if not image_map:
        image_map = await generate_storyboard_async(plan)

    selected_voice = plan.get('selected_voice', 'Deep_Voice_Man')
    use_subtitles = plan.get('use_subtitles', False)
    
    print(f"🎬 DÉBUT Rendu (Subs: {use_subtitles}) - Voix: {selected_voice}")

    def process_segment_sync(seg):
        seg_id = seg['segment_id']
        print(f"   ➤ [Seg {seg_id}] Démarrage...")
        
        source_image = image_map.get(str(seg_id)) or image_map.get(seg_id)
        if not source_image: return None

        try:
            # 1. AUDIO
            print(f"      🎵 [Seg {seg_id}] Audio...")
            audio_res = fal_client.subscribe(
                "fal-ai/minimax/speech-2.6-hd", 
                arguments={
                    "text": seg['voice_over'],
                    "voice_setting": {"voice_id": selected_voice, "emotion": "neutral", "speed": 1.1, "vol": 1.0},
                    "language_boost": "French",
                    "audio_setting": {"format": "mp3", "sample_rate": 32000}
                }
            )
            audio_url = audio_res['audio']['url']

            # 2. SOUS-TITRES (Wizper)
            srt_content = None
            if use_subtitles:
                print(f"      📝 [Seg {seg_id}] Sous-titres (Wizper)...")
                try:
                    wiz_res = fal_client.subscribe(
                        "fal-ai/wizper",
                        arguments={
                            "audio_url": audio_url,
                            "task": "transcribe",
                            "language": "fr"
                        }
                    )
                    # Utilisation de la nouvelle fonction de parsing qui gère 'chunks'
                    srt_content = json_to_srt(wiz_res)
                    
                    if srt_content:
                        print(f"      ✅ SRT généré ({len(srt_content)} chars)")
                    else:
                        print(f"      ⚠️ Wizper: SRT vide malgré réponse.")
                        
                except Exception as e:
                    print(f"      ⚠️ Erreur Wizper: {e}")

            # 3. VIDÉO (Kling)
            print(f"      🎥 [Seg {seg_id}] Vidéo...")
            video_res = fal_client.subscribe(
                "fal-ai/kling-video/v1.6/pro/image-to-video", 
                arguments={
                    "prompt": seg.get('action_prompt', ''),
                    "image_url": source_image,
                    "duration": "5",
                    "aspect_ratio": "9:16",
                    "negative_prompt": NEGATIVE_PROMPT
                }
            )
            
            return {
                "id": seg_id,
                "video_url": video_res['video']['url'],
                "audio_url": audio_url,
                "srt_content": srt_content
            }
        except Exception as e:
            print(f"   ❌ [Seg {seg_id}] ERREUR API: {e}")
            return None

    tasks = [loop.run_in_executor(None, process_segment_sync, s) for s in plan['segments']]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]