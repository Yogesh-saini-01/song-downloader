from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import zipfile
import shutil

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Select Songs</title>
</head>
<body>
    <h2>Enter Singer's Name:</h2>
    <form method="post">
        <input name="singer" required />
        <button type="submit">Search Songs</button>
    </form>
</body>
</html>
"""

HTML_SELECT = """
<h2>Songs of '{{ singer }}'</h2>
<form action="/download" method="post">
  {% for video in entries %}
    <input type="checkbox" name="video_urls" value="{{ video.webpage_url }}"> {{ video.title }}<br>
  {% endfor %}
  <input type="hidden" name="singer" value="{{ singer }}">
  <br>
  <input type="submit" value="Download Selected Songs">
</form>
<a href="/">Search again</a>
"""



@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        singer = request.form["singer"]
        query = f"ytsearch60:{singer} songs"
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            search_result = ydl.extract_info(query, download=False)
            entries = search_result.get('entries', [])
        return render_template_string(HTML_SELECT, entries=entries, singer=singer)
    return render_template_string(HTML_FORM)

@app.route("/download", methods=["POST"])
def download():
    selected_urls = request.form.getlist("video_urls")
    singer = request.form["singer"]
    
    if not selected_urls:
        return "No songs selected. <a href='/'>Go back</a>"

    for url in selected_urls:
        with yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{singer}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }) as ydl:
            ydl.download([url])

    return f"Downloaded {len(selected_urls)} songs successfully! Check your downloads folder.<br><a href='/'>Go back</a>"





    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                ydl.download([url])
            except Exception as e:
                print(f"Download failed: {e}")

    zip_path = "selected_songs.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(folder):
            zipf.write(os.path.join(folder, file), arcname=file)

    shutil.rmtree(folder)
    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
