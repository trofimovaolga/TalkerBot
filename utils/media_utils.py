import os
import sys
import subprocess
from PIL import Image
from pydub import AudioSegment

from config import cleanup_user_data, inference_path, custom_voice_filename



def get_center_crop(image_path: str) -> Image:
    """
    Opens an image from the given path and returns a centered square crop.
    
    Args:
        Path to the image file
    Returns:
        A PIL Image object with the centered square crop
    """
    with Image.open(image_path) as img:
        width, height = img.size
        min_dim = min(width, height)

        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim

        return img.crop((left, top, right, bottom)).resize((480, 480))
    

def generate_video(source: str, driving: str) -> dict:
    """
    Generates an animation by running LivePortrait inference script with the provided source and driving videos.

    Args:
        source: Path to the reference image
        driving: Path to the driving video
    Returns:
        A dictionary with either {'path': animation_path} on success or {'error': error_message} on failure
    """
    result = subprocess.run(
        [sys.executable, inference_path, "--source", source, "--driving", driving, "--flag_crop_driving_video"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return {'error': "Failed to generate animation. Error:\n" + result.stderr}

    p1 = os.path.splitext(os.path.basename(source))[0]
    p2 = os.path.splitext(os.path.basename(driving))[0]
    animation_path = f'./animations/{p1}--{p2}.mp4'
    if not os.path.exists(animation_path):
        return {'error': "Animation output not found. Something went wrong."}
    
    if cleanup_user_data:
        os.remove(source)
        os.remove(driving)
        os.remove(f"{os.path.splitext(driving)[0]}.pkl")

    return {'path': animation_path}


def convert_voice_tts(source: str, driving: str) -> dict:
    """
    Generates an audio by running TTS inference script with the provided source and driving audios.

    Args:
        source: Path to the reference audio
        driving: Path to the driving audio
    Returns:
        A dictionary with either {'path': voice_path} on success or {'error': error_message} on failure
    """
    p1 = os.path.splitext(os.path.basename(source))[0]
    p2 = os.path.splitext(os.path.basename(driving))[0]
    voice_path = f"./animations/{p1}-to-{p2}.wav"

    command = [
        "tts",
        "--out_path", voice_path,
        "--model_name", "voice_conversion_models/multilingual/vctk/freevc24",
        "--source_wav", source,
        "--target_wav", driving,
        "--use_cuda", "False"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return {'error': "Failed to convert voice. Error:\n" + result.stderr}

    return {'path': voice_path}


def convert_to_wav(input_file) -> dict:
    output_file = os.path.join(os.path.dirname(input_file), custom_voice_filename)
    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="wav")
        return {'path': output_file}
    except Exception as e:
        return {'error': "Failed to convert audio to wav format. Error:\n" + e}
    


def replace_voice_with_ffmpeg(video_path: str, target_voice: str, username: str) -> str:
    """
    Replace the audio in a video with a converted voice.
    
    Args:
        video_path: Path to the input video file
        target_voice: Target voice style for conversion
        username: Username for file naming
        
    Returns:
        Path to the new video file with replaced audio
    """
    orig_audio_path = os.path.join("./animations", f"{username}_orig_video_audio.wav")

    try:
        # Extract audio from video
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vn",  # no video
            "-acodec", "pcm_s16le",
            orig_audio_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Convert voice
        converted = convert_voice_tts(orig_audio_path, target_voice)
        if converted.get("error"):
            print(f'Failed to convert voice: {converted.get("error", "Unknown error")}')
            return

        new_video_path = os.path.join(os.path.dirname(video_path), "new_" + os.path.basename(video_path))
        # Replace audio in video
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-i", converted["path"],
            "-c:v", "copy",  # copy video stream
            "-map", "0:v:0",  # use original video
            "-map", "1:a:0",  # use new audio
            "-shortest",  # trim output to shortest stream (prevent silence at end)
            new_video_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return new_video_path
    
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg process error: {e.stderr.decode() if e.stderr else str(e)}")
        return None
    except Exception as e:
        print(f"Error replacing voice: {str(e)}")
        return None