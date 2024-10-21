import yt_dlp
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

def download_audio(url):
    video_id = url.replace('https://www.youtube.com/watch?v=', '')
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{video_id}.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return f'{video_id}.mp3'

def transcribe_audio(audio_file):

    device = "cuda:0" if torch.cuda.is_available() else "cpu"


    # Load model and processor
    model_id = "openai/whisper-large-v3"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True
    )

    result = pipe(audio_file)
    return result["text"]


    # processor = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
    # model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3")
    # model.to(device)

    # # Load audio
    # audio_input = processor(audio_file, return_tensors="pt").input_features

    # # Generate token ids
    # predicted_ids = model.generate(audio_input)

    # # Decode token ids to text
    # transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

    # return transcription[0]

# YouTube video URL
video_url = "https://www.youtube.com/watch?v=snX5YyflrGw"  # Replace with your desired YouTube video URL

# Download audio from YouTube
# audio_file = download_audio(video_url)
audio_file = "snX5YyflrGw.mp3"
# Transcribe the audio
transcription = transcribe_audio(audio_file)

print("Transcription:")
print(transcription)

video_id = video_url.replace('https://www.youtube.com/watch?v=', '')

with open(f'{video_id}.txt', 'w') as f:
  f.write(transcription)
