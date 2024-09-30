from flask import Flask, request, jsonify, send_file
from pytube import YouTube
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Charger les variables d'environnement à partir d'un fichier .env

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')  # Assurez-vous de définir votre clé API dans .env
BASE_URL = "https://www.googleapis.com/youtube/v3"

@app.route('/search', methods=['GET'])
def search_videos():
    titre = request.args.get('titre')
    if not titre:
        return jsonify({'error': 'Titre non fourni'}), 400

    search_url = f"{BASE_URL}/search"
    params = {
        'part': 'snippet',
        'q': titre,
        'type': 'video',
        'key': YOUTUBE_API_KEY,
        'maxResults': 10
    }

    response = requests.get(search_url, params=params)
    videos = response.json().get('items', [])

    results = []
    for video in videos:
        video_id = video['id']['videoId']
        title = video['snippet']['title']
        results.append({'videoId': video_id, 'title': title})

    return jsonify(results)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_id = data.get('videoId')
    media_type = data.get('mediaType', 'video')  # 'video' or 'audio'

    if not video_id:
        return jsonify({'error': 'videoId non fourni'}), 400

    file_path = None  # Initialiser file_path à None

    try:
        # Récupérer l'URL de la vidéo
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')

        if media_type == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
            file_extension = 'mp3'
        else:
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            file_extension = 'mp4'

        # Télécharger le fichier
        file_path = f"{yt.title}.{file_extension}"
        stream.download(filename=file_path)

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Nettoyage : Supprimer le fichier après l'envoi
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
