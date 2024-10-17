import os
from flask import Flask, render_template, request, redirect, url_for
import whisper
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/videos'

# Load Whisper Model
model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')


# Function to generate .srt format subtitles
def generate_srt(transcription):
    subtitles = []
    for i, segment in enumerate(transcription['segments']):
        start = segment['start']
        end = segment['end']
        text = segment['text'].strip()
        subtitles.append(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n")
    return "\n".join(subtitles)

# Format time in SRT time format
def format_time(seconds):
    ms = int((seconds * 1000) % 1000)
    s = int(seconds % 60)
    m = int((seconds // 60) % 60)
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# Route to handle video upload and transcription
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return redirect(request.url)

    file = request.files['video']
    
    if file.filename == '':
        return redirect(request.url)
    
    # Save uploaded video to static/videos folder
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(video_path)
    
    # Extract audio and save it as .wav
    video = VideoFileClip(video_path)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav')
    video.audio.write_audiofile(audio_path)
    
    # Transcribe the audio with Whisper (with timestamps)
    transcription = model.transcribe(audio_path)
    
    # Generate SRT file
    srt_content = generate_srt(transcription)
    srt_path = os.path.join(app.config['UPLOAD_FOLDER'], 'subtitles.srt')
    with open(srt_path, 'w') as srt_file:
        srt_file.write(srt_content)
    
    return render_template('result.html', video_filename=file.filename, subtitle_filename='subtitles.srt')

if __name__ == '__main__':
    app.run(debug=True)
