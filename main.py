from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ytmusicapi import YTMusic
import yt_dlp
import uvicorn

app = FastAPI()
yt = YTMusic()

# Allows any device in the house to talk to your code
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_home():
    # This serves your index.html file to anyone who visits the link
    return FileResponse("index.html")

@app.get("/search")
def search(q: str):
    results = yt.search(q, filter="songs")
    songs = []
    for s in results:
        songs.append({
            "title": s['title'],
            "artist": s['artists'][0]['name'] if s['artists'] else "Unknown",
            "id": s['videoId'],
            "thumb": s['thumbnails'][-1]['url']
        })
    return songs

@app.get("/get_audio")
def get_audio(id: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={id}", download=False)
        return {"url": info['url']}

if __name__ == "__main__":
    # host="0.0.0.0" is the secret to making it work on other devices
    uvicorn.run(app, host="0.0.0.0", port=8000)