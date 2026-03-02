# Localization strings for the Caption Editor app

# Set the active language here: "en" or "uk"
LANGUAGE = "uk"

STRINGS = {
    "en": {
        # Header and login
        "app_title": "Caption Editor",
        "please_log_in": "Please log in via Hugging Face",
        "logged_in_as": "Logged in as",
        "log_in_button": "Log in",
        
        # Main interface
        "next_button": "Go to next video",
        "add_entry_button": "Add Entry",
        "editing_complete_checkbox": "Captions for this video are complete",
        "show_incomplete_only_checkbox": "Only show videos with incomplete captions",
        
        # Table headers
        "header_start": "Start",
        "header_text": "Text",
        "header_end": "End",
        "header_aligned": "Aligned",
        
        # Edit form
        "edit_caption_title": "Edit Caption Entry",
        "start_time_label": "Start Time (seconds)",
        "caption_text_label": "Caption Text",
        "caption_text_placeholder": "Enter caption text...",
        "end_time_label": "End Time (seconds)",
        "insert_time_button": "Insert",
        "goto_time_button": "Go to",
        "save_entry_button": "Save Entry",
        "update_entry_button": "Update Entry",
        "add_entry_button_form": "Add Entry",
        "cancel_button": "Cancel",
        "preview_button": "Preview ▶",
        "preview_times_equal": "Cannot preview: start and end times are equal",
        "preview_invalid_times": "Cannot preview: start time must be less than end time",

        # Playback controls
        "playback_controls_title": "Playback Controls",
        "seek_back_1s": "-1s",
        "seek_back_100ms": "-100ms",
        "play_button": "Play",
        "pause_button": "Pause",
        "seek_forward_100ms": "+100ms",
        "seek_forward_1s": "+1s",
        "speed_label": "Speed:",

        # Messages
        "please_sign_in": "Please sign in to save changes",
        "start_less_than_end": "Start time must be less than end time",
        "text_cannot_be_empty": "Text cannot be empty",
        "save_successful": "Save successful!",
        "save_failed": "Save failed:",
        "invalid_time_format": "Invalid time format:",
        "error": "Error:",
        "all_videos_transcribed": "Save cancelled: All videos transcribed",
        "change_video_completion_status_success": "Video completion status successfully changed",
        "show_incomplete_only_change": "List of accessible videos successfully changed",
    },
    "uk": {
        # Header and login
        "app_title": "Редактор субтитрів",
        "please_log_in": "Будь ласка, увійдіть через Hugging Face",
        "logged_in_as": "Ви увійшли як",
        "log_in_button": "Увійти",
        
        # Main interface
        "next_button": "Перейти до наступного відео",
        "add_entry_button": "Додати субтитр",
        "editing_complete_checkbox": "Розмітка цього відео готова",
        "show_incomplete_only_checkbox": "Показувати лише відео із незавершеною розміткою",

        # Table headers
        "header_start": "Початок",
        "header_text": "Текст",
        "header_end": "Кінець",
        "header_aligned": "Вирівняно",
        
        # Edit form
        "edit_caption_title": "Редагувати субтитр",
        "start_time_label": "Час початку (секунди)",
        "caption_text_label": "Текст субтитру",
        "caption_text_placeholder": "Введіть текст субтитру...",
        "end_time_label": "Час кінця (секунди)",
        "insert_time_button": "Вставити",
        "goto_time_button": "Перейти",
        "save_entry_button": "Зберегти запис",
        "update_entry_button": "Оновити запис",
        "add_entry_button_form": "Додати запис",
        "cancel_button": "Скасувати",
        "preview_button": "Превʼю ▶",
        "preview_times_equal": "Превʼю недоступне: час початку та кінця однакові",
        "preview_invalid_times": "Превʼю недоступне: час початку має бути менше часу кінця",

        # Playback controls
        "playback_controls_title": "Керування відтворенням",
        "seek_back_1s": "-1с",
        "seek_back_100ms": "-100мс",
        "play_button": "Грати",
        "pause_button": "Пауза",
        "seek_forward_100ms": "+100мс",
        "seek_forward_1s": "+1с",
        "speed_label": "Швидкість:",

        # Messages
        "please_sign_in": "Будь ласка, увійдіть, щоб зберегти зміни",
        "start_less_than_end": "Час початку повинен бути менше часу кінця",
        "text_cannot_be_empty": "Текст не може бути порожнім",
        "save_successful": "Успішно збережено!",
        "save_failed": "Помилка збереження:",
        "invalid_time_format": "Невірний формат часу:",
        "error": "Помилка:",
        "all_videos_transcribed": "Відміна збереження: Усі відео розмічено",
        "change_video_completion_status_success": "Статус відео успішно змінено",
        "show_incomplete_only_change": "Список доступних відео успішно змінено",
    }
}


def get_string(key):
    """Get localized string by key"""
    return STRINGS[LANGUAGE].get(key, key)
