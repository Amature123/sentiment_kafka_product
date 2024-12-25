import re

def clean_message_content(raw_content):
    """
    Remove the lightbox configuration JSON from message content using regex.
    
    Args:
        raw_content (str): Raw message content from scraping
        
    Returns:
        str: Cleaned message content
    """
    # Pattern to match the entire lightbox JSON object
    pattern = r'\{\n\t+\"lightbox_.*?\"Toggle sidebar\"\n\t+\}'
    
    # Remove the JSON object and strip whitespace
    cleaned = re.sub(pattern, '', raw_content, flags=re.DOTALL).strip()
    return cleaned

# Example usage:
test_content = """Mấy con card hết thời bú điện như nước thì chắc đem rã xác lấy vàng thôi nhỉ {\n\t\t\t\t"lightbox_close": "Close",\n\t\t\t\t"lightbox_next": "Next",\n\t\t\t\t"lightbox_previous": "Previous",\n\t\t\t\t"lightbox_error": "The requested content cannot be loaded. Please try again later.",\n\t\t\t\t"lightbox_start_slideshow": "Start slideshow",\n\t\t\t\t"lightbox_stop_slideshow": "Stop slideshow",\n\t\t\t\t"lightbox_full_screen": "Full screen",\n\t\t\t\t"lightbox_thumbnails": "Thumbnails",\n\t\t\t\t"lightbox_download": "Download",\n\t\t\t\t"lightbox_share": "Share",\n\t\t\t\t"lightbox_zoom": "Zoom",\n\t\t\t\t"lightbox_new_window": "New window",\n\t\t\t\t"lightbox_toggle_sidebar": "Toggle sidebar"\n\t\t\t}"""

cleaned_content = clean_message_content(test_content)
print(f"Cleaned content: {cleaned_content}")