import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# This allows your Netlify site to access this backend without security blocks
CORS(app)

# Optimization: Keep the yt_dlp options outside the function to save memory
YDL_OPTS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    # This prevents the server from trying to download the whole file
    'force_generic_extractor': False, 
}

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # We search for the top 10 results
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = []
            for entry in info['entries']:
                results.append({
                    'id': entry['id'],
                    'title': entry['title'],
                    'artist': entry.get('uploader', 'Unknown Artist'),
                    'duration': entry.get('duration')
                })
            return jsonify(results)
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_audio', methods=['GET'])
def get_audio():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "No ID provided"}), 400

    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            # We want the direct stream URL so the browser plays it
            return jsonify({"url": info['url']})
    except Exception as e:
        print(f"Audio fetch error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # CRITICAL: Hosting services tell the app which port to use via an Environment Variable
    # If 'PORT' isn't set, it defaults to 8000 (for your local testing)
    port = int(os.environ.get("PORT", 8000))
    # '0.0.0.0' makes the server accessible to the outside world
    app.run(host='0.0.0.0', port=port)
