import os, json, random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_production_plan(user_idea, nb_segments, style_preset="realistic_cinematic", camera_type="cinematic", voice_gender="male", voice_vibe="neutral"):
    
    project_seed = random.randint(100000, 999999)

    # --- MAPPING VOIX ---
    voice_map = {
        "male": { "neutral": "Patient_Man", "epic": "Deep_Voice_Man", "dynamic": "Young_Knight", "emotional": "Elegant_Man" },
        "female": { "neutral": "Wise_Woman", "epic": "Inspirational_girl", "dynamic": "Lively_Girl", "emotional": "Lovely_Girl" }
    }
    selected_voice = voice_map.get(voice_gender, voice_map["male"]).get(voice_vibe, "Deep_Voice_Man")

    # --- MAPPING STYLE VISUEL ---
    # Styles ultra-détaillés pour garantir la qualité "Masterpiece"
    style_modifiers = {
        "realistic_cinematic": "Cinematic film still, shot on Arri Alexa 65, Panavision anamorphic lenses, photorealistic 8k, highly detailed skin texture, volumetric lighting, color graded, film grain, masterpiece, depth of field.",
        "3d_cartoon": "3D animated feature film still, Pixar Disney style, Redshift render, cute stylized character, subsurface scattering, vibrant colors, expressive eyes, global illumination, intricate details, 8k resolution.",
        "anime_manga": "High budget anime film still, Makoto Shinkai style, detailed background art, dramatic lighting, hand drawn textures, 4k crisp lines, atmospheric, emotional, wallpaper quality.",
        "illustration_book": "Storybook illustration, textured paper, visible brushstrokes, watercolor and ink, whimsical, warm color palette, golden ratio composition, highly detailed, fantasy art."
    }
    current_visual_style = style_modifiers.get(style_preset, style_modifiers["realistic_cinematic"])

    # --- MAPPING CAMÉRA (Kling) ---
    camera_instructions = {
        "cinematic": "Slow cinematic push-in or parallax movement revealing depth.",
        "zoom_in": "Slow smooth camera ZOOM IN focusing tightly on the subject.",
        "zoom_out": "Slow smooth camera ZOOM OUT revealing the scale of the environment.",
        "pan_right": "Steady cinematic PAN RIGHT tracking the action.",
        "static": "Completely STATIC camera frame, emphasizing internal tension.",
        "handheld": "Handheld camera shake, dynamic, immersive documentary style realism.",
        "drone": "High angle aerial drone shot, establishing massive scale."
    }
    current_camera_instruction = camera_instructions.get(camera_type, camera_instructions["cinematic"])

    # --- LE MASTER PROMPT SYSTÈME (VERSION "SCENE INTELLIGENCE") ---
    system_prompt = f"""
    Tu es un Réalisateur de Cinéma expert et un Prompt Engineer d'élite.
    Ta mission est de transformer l'idée : "{user_idea}" en un storyboard vidéo de {nb_segments} plans, visuellement varié et cohérent.

    ### 1. CRÉATION DE L'ADN DU PERSONNAGE (CHARACTER DNA)
    Défini d'abord le `character_dna` (Description physique complète en Anglais).
    - Inclus : Âge, Genre, Ethnie, Coiffure, Barbe (précise), Cicatrice, Vêtements (matière/couleur).
    - Ce bloc est ta "Bible". Il ne doit jamais changer.

    ### 2. LOGIQUE DE DÉCOUPAGE (SCENE TYPES) - TRES IMPORTANT
    Pour éviter l'ennui visuel, tu dois choisir un **FOCUS** différent pour chaque segment.
    Ne montre PAS le visage du personnage sur toutes les images. C'est interdit.

    Tu as 3 types de scènes possibles :
    
    * **TYPE A : ESTABLISHING (Le Décor)**
        * *Quand l'utiliser :* Pour situer l'action, montrer une immensité, une tour, une ville.
        * *Visuel :* Plan Large (Extreme Wide Shot). Le personnage est une silhouette lointaine ou absent.
        * *Prompt construction :* `{current_visual_style}, majestic landscape of [LIEU], atmospheric lighting, massive scale. (Tiny silhouette of [character_dna] seen from back).`

    * **TYPE B : ACTION / OBJECT (Le Détail)**
        * *Quand l'utiliser :* Pour une action physique (taper au clavier, attraper une épée, ouvrir une porte).
        * *Visuel :* Gros plan sur les MAINS ou l'OBJET (Extreme Close-Up). PAS DE VISAGE.
        * *Prompt construction :* `{current_visual_style}, Extreme close-up on [HANDS/OBJECT], sparks flying, motion blur, intense detail, texture focus.`

    * **TYPE C : CHARACTER (L'Émotion)**
        * *Quand l'utiliser :* Pour une réaction, un dialogue intérieur, une peur.
        * *Visuel :* Plan Poitrine ou Gros Plan Visage.
        * *Prompt construction :* `{current_visual_style}, [character_dna], intense expression, looking at [TARGET], cinematic lighting on face.`

    **RÈGLE D'OR :** Tu dois ALTERNER les types. Jamais 3 fois "TYPE C".

    ### 3. RÈGLES AUDIO & MUSIQUE
    - **Audio :** Français. **15 à 20 mots** par segment. Décris l'action ou l'ambiance. Pas de phrases vides.
    - **Musique :** Prompt instrumental Anglais pour AceStep (ex: "Dark synthwave, pulsing bass").

    ### STRUCTURE JSON ATTENDUE ###
    {{
      "project_title": "Titre",
      "consistency_seed": {project_seed},
      "selected_voice": "{selected_voice}",
      "style_preset": "{style_preset}",
      "music_prompt": "Ambiance musicale globale...",
      "character_dna": "Full description (used heavily in Type C)...",
      "segments": [
        {{
          "segment_id": 1,
          "scene_type": "TYPE A (ESTABLISHING) ou TYPE B (ACTION) ou TYPE C (CHARACTER)",
          "voice_over": "Texte FR (15-20 mots)...",
          "visual_prompt": "Prompt construit selon la logique du TYPE choisi ci-dessus...",
          "action_prompt": "{current_camera_instruction}, description du mouvement..."
        }},
        {{
          "segment_id": 2,
          "scene_type": "...",
          "voice_over": "Texte FR (15-20 mots)...",
          "visual_prompt": "Prompt varié (angle différent du précédent)...",
          "action_prompt": "..."
        }}
        // Génère exactement {nb_segments} segments.
      ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7 # Créativité nécessaire pour varier les plans
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Err Orchestrator: {e}")
        return None