# 🎬 AI Short Generator (LeLabs)

**Générateur de vidéos courtes (Shorts/Reels) entièrement automatisé par IA.**

Ce projet est une application web (Flask) qui orchestre plusieurs modèles d'IA de pointe pour transformer une simple idée textuelle en une vidéo complète de 15 à 45 secondes, incluant :
* Scénario et découpage technique (OpenAI GPT-4o)
* Images hyper-réalistes cohérentes (Flux Schnell via Fal.ai)
* Animation vidéo (Kling Pro via Fal.ai)
* Voix off ultra-réaliste (Minimax via Fal.ai)
* Musique de fond adaptative (AceStep via Fal.ai)
* Sous-titres automatiques incrustés (Wizper via Fal.ai + FFmpeg)

---

## ✨ Fonctionnalités

* **Orchestration "Director Mode"** : L'IA agit comme un réalisateur, définissant les plans (Large, Action, Gros plan) et garantissant la variété visuelle.
* **Cohérence Personnage (Character DNA)** : Maintient l'apparence du protagoniste (vêtements, visage) tout au long de la vidéo grâce à des prompts structurés.
* **Pipeline Complet** : De la génération du script au montage final `.mp4`.
* **Post-Production Automatisée** :
    * Synchronisation audio/vidéo stricte.
    * Incrustation de sous-titres (Hardsub style réseaux sociaux).
    * Mixage audio (Ducking) pour que la musique ne couvre pas la voix.
* **Interface Web** : Tableau de bord pour configurer le style, la voix, et prévisualiser/régénérer les images avant le rendu final.

---

## 🛠️ Pré-requis

* **Python 3.11+**
* **FFmpeg** installé et ajouté au PATH système (Indispensable pour l'assemblage).
* Clés API pour :
    * [OpenAI](https://platform.openai.com/) (GPT-4o)
    * [Fal.ai](https://fal.ai/) (Flux, Kling, Minimax, AceStep, Wizper)

---

## 🚀 Installation (Local)

1.  **Cloner le dépôt :**
    ```bash
    git clone [https://github.com/P2Enjoy/lelabs_ai-short-generator.git](https://github.com/P2Enjoy/lelabs_ai-short-generator.git)
    cd lelabs_ai-short-generator
    ```

2.  **Créer un environnement virtuel (recommandé) :**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurer les variables d'environnement :**
    Créez un fichier `.env` à la racine du projet et ajoutez vos clés :
    ```env
    OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
    FAL_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxx
    ```

5.  **Lancer l'application :**
    ```bash
    python app.py
    ```
    Ouvrez votre navigateur sur `http://127.0.0.1:5000`.

---

## 🐳 Installation (Docker)

Le projet est prêt pour Docker. L'image inclut Python et FFmpeg pré-configurés.

1.  **Construire l'image :**
    ```bash
    docker build -t ai-short-generator .
    ```

2.  **Lancer le conteneur :**
    Assurez-vous d'avoir votre fichier `.env` prêt.
    ```bash
    docker run -p 5000:5000 --env-file .env ai-short-generator
    ```
    L'application sera accessible sur `http://localhost:5000`.

---

## 🎮 Utilisation

1.  **Page Config (`/config`)** :
    * Entrez votre idée (ex: "Un samouraï cyberpunk médite sous la pluie").
    * Choisissez le style visuel, le mouvement de caméra, la voix et la durée.
    * Activez/Désactivez la Musique et les Sous-titres.

2.  **Page Éditeur (`/editor`)** :
    * L'IA génère un plan de production (3 à 9 scènes).
    * **Générer Storyboard** : Crée les images de référence avec Flux.
    * *Optionnel* : Cliquez sur une image pour la sélectionner et la régénérer si elle ne vous plaît pas.
    * Vous pouvez modifier le texte de la Voix Off directement.

3.  **Rendu Final (`/process`)** :
    * Cliquez sur "Lancer le Rendu".
    * Le système génère l'audio, la vidéo (Kling), la musique, transcrit les sous-titres et assemble le tout avec FFmpeg.
    * Téléchargez votre vidéo finale.

---

## 📂 Structure du Projet

* `app.py` : Serveur Flask et points d'entrée API.
* `orchestrator.py` : Le "Cerveau" (GPT-4o) qui écrit le script et les prompts techniques.
* `generator.py` : Gestion des appels API vers Fal.ai (Images, Vidéo, Audio, Musique, Subs).
* `assembler.py` : Script de montage vidéo automatisé (FFmpeg wrapper).
* `templates/` : Interface utilisateur (HTML/JS).
* `static/outputs/` : Dossier où sont sauvegardées les vidéos générées.

---

## ⚠️ Notes Importantes

* **Coûts API** : La génération de vidéo (Kling Pro) et d'images (Flux) coûte des crédits Fal.ai. Surveillez votre consommation.
* **Temps de Rendu** : La génération vidéo prend du temps (environ 2-3 minutes pour une vidéo de 15s). Ne fermez pas la fenêtre pendant le processus.
* **Windows** : Si vous n'utilisez pas Docker, assurez-vous que FFmpeg est correctement installé dans vos variables d'environnement système.

---

**Développé par P2Enjoy / LeLabs**
