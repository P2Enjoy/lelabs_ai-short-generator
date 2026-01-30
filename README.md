# 🎬 AI Short Generator (LeLabs)

**Générateur de vidéos courtes (Shorts/Reels) entièrement automatisé par IA.**

Ce projet est une application web (Flask) capable de transformer une simple idée textuelle en une vidéo complète. Il orchestre plusieurs modèles d'IA (GPT-4, Flux, Kling, Minimax) et assemble le tout via FFmpeg.

**Particularité Architecturelle :**
Cette application est conçue pour fonctionner de pair avec **`lelabs_api-proxy`**. Toutes les requêtes sortantes (OpenAI, Fal.ai) passent par ce proxy local pour la gestion centralisée des quotas et de la sécurité.

---

## ✨ Fonctionnalités

* **Scénarisation IA** : GPT-4o ("Director Mode") écrit le script et les prompts techniques.
* **Visuels Cohérents** : Flux Schnell génère les images avec un maintien de l'apparence du personnage (Character DNA).
* **Animation Vidéo** : Kling Pro anime les images statiques (5s par plan).
* **Audio & Lip-Sync** : Voix off ultra-réaliste (Minimax) et musique d'ambiance (AceStep).
* **Post-Production Auto** : Montage, mixage audio et incrustation de sous-titres via FFmpeg.

---

## 📋 Pré-requis

Avant de commencer, assurez-vous d'avoir installé :

1.  **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Indispensable).
2.  **Git**.

---

## 🏗️ Installation et Architecture

Pour que l'application fonctionne avec Docker Compose, vous devez respecter une structure de dossiers précise, car le fichier de configuration va chercher le code du proxy dans le dossier voisin.

### 1. Structure des dossiers attendue
Créez un dossier parent (ex: `LELABS_STACK`) et clonez les deux dépôts à l'intérieur :

```text
LELABS_STACK/
├── lelabs_ai-short-generator/   <-- Ce dépôt (Application Vidéo)
│   ├── docker-compose/          <-- Contient le fichier docker-compose.yml
│   ├── app.py
│   └── ...
│
└── lelabs_api-proxy/            <-- Le dépôt d'Infrastructure (Proxy)
    ├── quota/
    └── ...

```

### 2. Cloner les dépôts

```bash
# Dans votre dossier LELABS_STACK
git clone [https://github.com/P2Enjoy/lelabs_ai-short-generator.git](https://github.com/P2Enjoy/lelabs_ai-short-generator.git)
git clone [https://github.com/P2Enjoy/lelabs_api-proxy.git](https://github.com/P2Enjoy/lelabs_api-proxy.git)

```

### 3. Configuration des Clés API (.env)

Créez un fichier `.env` à la racine du dossier **`lelabs_ai-short-generator`**.
⚠️ **Ce fichier ne doit jamais être commité sur GitHub.**

```env
# Clés API réelles (utilisées par le système)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
FAL_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Configuration du Proxy (Ne pas modifier pour Docker)
OPENAI_BASE_URL=http://proxy-app:8000/v1
FAL_HOST=proxy-app:8000
FAL_G_INSECURE=true

```

---

## 🚀 Lancer l'application (Docker)

Nous utilisons `docker-compose` pour lancer simultanément l'application vidéo et le proxy, et les relier via un réseau privé.

1. Ouvrez votre terminal dans le dossier **`lelabs_ai-short-generator`**.
2. Lancez la commande suivante (en pointant vers le fichier situé dans le sous-dossier) :

```bash
docker-compose -f docker-compose/docker-compose.yml up --build

```

**Ce que fait cette commande :**

* Construit l'image du Générateur (avec Python et FFmpeg).
* Construit l'image du Proxy (en cherchant le code dans le dossier voisin `../lelabs_api-proxy`).
* Démarre les deux services.
* Configure le routage pour que le Générateur parle au Proxy.

---

## 🎮 Utilisation

Une fois que les logs indiquent que les serveurs tournent :

1. Ouvrez votre navigateur sur : **[http://localhost:5000/config](https://www.google.com/search?q=http://localhost:5000/config)**
2. Entrez votre idée de vidéo.
3. Configurez le style et lancez la génération.

**Vérification de l'intégration :**
Regardez vos logs terminaux pendant la génération. Vous devriez voir des lignes venant de `proxy-app` indiquant :
`🔄 PROXY (Bypass): v1/chat/completions -> ...`
Cela confirme que votre trafic passe bien par l'infrastructure interne.

---

## 🛠️ Dépannage

* **Erreur `connection refused` ou `host not found**` : Vérifiez que le conteneur `proxy-app` est bien lancé.
* **Erreur FFmpeg** : Si la vidéo finale échoue, assurez-vous que le Dockerfile a bien installé `ffmpeg` (c'est inclus par défaut dans l'image fournie).
* **Problème de chemins (Build Context)** : Si Docker ne trouve pas le proxy ("build context not found"), vérifiez impérativement que vos deux dossiers (`lelabs_ai-short-generator` et `lelabs_api-proxy`) sont bien côte à côte dans le même dossier parent.

---

**Développé par P2Enjoy / LeLabs**

```
