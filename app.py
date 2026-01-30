from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, time, asyncio
from orchestrator import generate_production_plan
from generator import produce_short_async, generate_storyboard_async, generate_music_track
from assembler import assemble_video

app = Flask(__name__)
app.secret_key = "SECRET_KEY_PRO_STUDIO"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/config')
def config():
    return render_template('config.html', mode=request.args.get('mode', 'oneshot'))

@app.route('/api/init', methods=['POST'])
def api_init():
    data = request.json
    
    # Récupération des options standards
    idea = data.get('idea')
    segments = int(data.get('segments', 3))
    style = data.get('style', 'realistic_cinematic')
    camera = data.get('camera', 'cinematic') 
    voice_gender = data.get('voice_gender', 'male')
    voice_vibe = data.get('voice_vibe', 'neutral')

    # Récupération des options Post-Prod
    use_music = data.get('use_music', False)
    use_subtitles = data.get('use_subtitles', False)

    # L'orchestrateur va aussi décider de l'ambiance musicale
    plan = generate_production_plan(
        user_idea=idea, 
        nb_segments=segments,
        style_preset=style,
        camera_type=camera,
        voice_gender=voice_gender,
        voice_vibe=voice_vibe
    )
    
    # On injecte les préférences utilisateur dans le plan pour plus tard
    plan['use_music'] = use_music
    plan['use_subtitles'] = use_subtitles

    session['plan'] = plan
    session.pop('generated_images', None)
    
    return jsonify(plan)

@app.route('/editor')
def editor():
    if 'plan' not in session: return redirect(url_for('config'))
    return render_template('editor.html', plan=session['plan'])

@app.route('/api/update_plan', methods=['POST'])
def update_plan():
    data = request.json
    session['plan'] = data['plan']
    return jsonify({"status": "ok"})

@app.route('/api/storyboard', methods=['POST'])
def api_storyboard():
    plan = session.get('plan')
    data = request.json or {}
    indices = data.get('indices', None) 
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    new_images = loop.run_until_complete(generate_storyboard_async(plan, indices=indices))
    
    current_images = session.get('generated_images', {})
    if not isinstance(current_images, dict): current_images = {}
    current_images.update(new_images)
    
    final_images = {str(k): v for k, v in current_images.items()}
    session['generated_images'] = final_images
    
    return jsonify(final_images)

@app.route('/process')
def process():
    if 'plan' not in session: return redirect(url_for('config'))
    return render_template('process.html')

@app.route('/api/render', methods=['POST'])
def api_render():
    plan = session.get('plan')
    saved_images = session.get('generated_images')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 1. Génération Vidéo + Audio + Sous-titres (si demandés)
    assets = loop.run_until_complete(produce_short_async(plan, image_map=saved_images))
    
    # 2. Génération Musique (si demandée) - UNE SEULE PISTE pour tout le projet
    music_url = None
    if plan.get('use_music') and plan.get('music_prompt'):
        # On demande une durée approximative (nb_segments * 5s + marge)
        duration_approx = len(plan['segments']) * 6 
        music_url = loop.run_until_complete(generate_music_track(plan['music_prompt'], duration=duration_approx))

    # 3. Assemblage Final
    filename = f"video_{int(time.time())}.mp4"
    filepath = os.path.join("static", "outputs", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    assemble_video(assets, filepath, music_url=music_url)
    
    return jsonify({"url": f"/static/outputs/{filename}"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)