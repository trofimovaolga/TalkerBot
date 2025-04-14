import os
import sys
import subprocess
from PIL import Image
from config import cleanup_user_data, inference_path



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