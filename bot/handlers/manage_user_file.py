import os

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from bot.bot_manager import BotManager
from config import uploads_path, max_duration, ADD_DRIVING_VIDEO, ADD_VOICE, cleanup_animations, custom_voice_filename
from utils.media_utils import get_center_crop, generate_video, convert_to_wav, replace_voice_with_ffmpeg



async def add_ref_image_handler(update: Update, context: CallbackContext) -> int:
    """
    Handles the user's uploaded reference image.

    - Accepts a photo from the user.
    - Saves and center-crops the image.
    - Stores the image path in user_data for future use.

    Returns:
        int: The next conversation state (ADD_DRIVING_VIDEO or END).
    """
    username = update.effective_user.username
    manager = BotManager()
    lang = manager.get_user_language(username)

    if not manager.is_allowed_user(username):
        manager.logger.warning(f'{username} tried issuing a command but was not allowed.')
        await update.message.reply_text(manager.get_message("access_denied"))
        return ConversationHandler.END

    if update.message.photo:
        file_content = await update.message.photo[-1].get_file()
        file_name = os.path.basename(file_content.file_path)
    else:
        message = manager.get_message("unsupported_file_type", lang)
        await update.message.reply_text(message)
        return ConversationHandler.END

    file_path = os.path.join(uploads_path, username, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        await file_content.download_to_drive(file_path)
        get_center_crop(file_path).save(file_path)
        manager.logger.info(f'File from {username} temporarily loaded to {file_path}.')
        context.user_data["ref_img_file"] = file_path
        message = manager.get_message("got_img", lang)
        await update.message.reply_text(message)
        return ADD_DRIVING_VIDEO

    except Exception as e:
        message = manager.get_message('file_failed', lang).format(e=e)
        await update.message.reply_text(message)
        manager.logger.error(f"File processing failed: {e}")
        return ConversationHandler.END
    

async def add_driving_video_handler(update: Update, context: CallbackContext) -> int:
    """
    Handles the user's uploaded video or video note to drive animation.

    - Downloads the video.
    - Runs video generation using a previously uploaded reference image.
    - Sends the resulting animation back to the user.

    Returns:
        int: ConversationHandler.END when processing is complete or fails.
    """
    username = update.effective_user.username
    manager = BotManager()
    lang = manager.get_user_language(username)

    if update.message.video:
        file_content = await update.message.video.get_file()
        file_name = os.path.basename(file_content.file_path)

    elif update.message.video_note:
        if update.message.video_note.duration > max_duration:
            message = manager.get_message('long_video', lang).format(max_duration=max_duration)
            await update.message.reply_text(message)
            return ADD_DRIVING_VIDEO
        file_content = await update.message.video_note.get_file()
        file_name = os.path.basename(file_content.file_path)

    else:
        print(f'{update.message=}')
        message = manager.get_message("unsupported_file_type", lang)
        await update.message.reply_text(message)
        return ADD_DRIVING_VIDEO

    file_path = os.path.join(uploads_path, username, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        await file_content.download_to_drive(file_path)
        manager.logger.info(f'File from {username} temporarily loaded to {file_path}.')
        message = manager.get_message("got_video", lang)
        await update.message.reply_text(message)

        ref_img_file = context.user_data.get('ref_img_file', None)
        if not ref_img_file:
            message = manager.get_message("no_img", lang)
            await update.message.reply_text(message)
            return ConversationHandler.END

        result = generate_video(ref_img_file, file_path)
        if result.get('error'):
            manager.logger.error(f"Generation failed: {result.get('error')}")
            message = manager.get_message("generation_failed", lang)
            await update.message.reply_text(message)
            return ConversationHandler.END
        else:
            animation_path = result["path"]

        # Voice settings
        cur_voice = manager.get_user_voice(username)
        if cur_voice != "orig":
            target_voice = os.path.join("./resources", cur_voice + ".wav") if "male" in cur_voice else os.path.join(uploads_path, username, custom_voice_filename)
            message = manager.get_message("wait_audio_convertion", lang)
            await update.message.reply_text(message)
            new_video_path = replace_voice_with_ffmpeg(
                video_path=animation_path, 
                target_voice=target_voice, 
                username=username
            )
            if not new_video_path:
                message = manager.get_message("failed_audio_convertion", lang)
                await update.message.reply_text(message)
            else:
                animation_path = new_video_path


        with open(animation_path, 'rb') as video:
            await update.message.reply_video_note(video)
        message = manager.get_message("send_video", lang)
        await update.message.reply_text(message)

        if cleanup_animations:
            os.remove(animation_path)
            os.remove(f"{os.path.splitext(animation_path)[0]}_concat.mp4")

        return ConversationHandler.END

    except Exception as e:
        manager.logger.error(f"File processing failed: {e}")
        message = manager.get_message('generation_failed', lang)
        await update.message.reply_text(message)
        return ConversationHandler.END


async def cancel_handler(update: Update, context: CallbackContext) -> int:
    """
    Cancels the current operation and ends the conversation.

    Returns:
        int: ConversationHandler.END to exit the conversation.
    """
    username = update.effective_user.username

    manager = BotManager()
    lang = manager.get_user_language(username)
    message = manager.get_message('cancel', lang)
    await update.message.reply_text(message)
    return ConversationHandler.END


async def ask_voice_handler(update: Update, context: CallbackContext) -> int:
    username = update.effective_user.username

    manager = BotManager()
    lang = manager.get_user_language(username)

    if not manager.is_allowed_user(username):
        manager.logger.warning(f'{username} tried issuing a command but was not allowed.')
        await update.message.reply_text(manager.get_message("access_denied"))
        return ConversationHandler.END
    
    message = manager.get_message('send_voice', lang)
    await update.message.reply_text(message)
    return ADD_VOICE


async def add_voice_handler(update: Update, context: CallbackContext) -> int:
    username = update.effective_user.username
    manager = BotManager()
    lang = manager.get_user_language(username)

    if update.message.voice:
        manager.logger.debug('Got voice')
        file_content = await update.message.voice.get_file()
        file_name = os.path.basename(file_content.file_path)
    elif update.message.audio:
        manager.logger.debug('Got audio')
        file_content = await update.message.audio.get_file()
        file_name = os.path.basename(file_content.file_path)
    elif update.message.document and 'audio' in update.message.document.mime_type:
        manager.logger.debug('Got audio doc')
        file_content = await update.message.document.get_file()
        file_name = os.path.basename(file_content.file_path)
    else:
        manager.logger.debug(f'Unsupported format: {update.message=}')
        message = manager.get_message("unsupported_file_type", lang)
        await update.message.reply_text(message)
        return ADD_VOICE

    file_path = os.path.join(uploads_path, username, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        await file_content.download_to_drive(file_path)
        wav_file = convert_to_wav(file_path)
        if wav_file.get('error', None):
            manager.logger.error(f"File {file_path} from {username} was not converted to wav.")
        else:
            manager.logger.info(f'Removing audio file {file_path}')
            os.remove(file_path)
            file_path = wav_file.get('path')
        
        manager.logger.info(f'File from {username} temporarily loaded to {file_path}.')

        manager.set_user_voice(username, custom_voice_filename)
        manager.logger.info(f"{username} set custom {file_path} voice.")
        message = manager.get_message('voice_is_set', lang)
        await update.message.reply_text(message)
        return ConversationHandler.END

    except Exception as e:
        message = manager.get_message('file_failed', lang).format(e=e)
        await update.message.reply_text(message)
        manager.logger.error(f"File processing failed: {e}")
        return ConversationHandler.END