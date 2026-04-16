from bs4 import BeautifulSoup
from email.message import Message

def get_clean_body(body):
    soup = BeautifulSoup(body, "html.parser")
    
    # Remove script and style tags completely
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n")
    
    # Clean up whitespace
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

def get_email_body(msg: Message) -> str:
    """
    Extracts the plain text body from an email message object.
    """
    if msg.is_multipart():
        for part in msg.walk():
            # Find the first plain text part
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
            # If no plain text, find the first HTML part as a fallback
            elif part.get_content_type() == 'text/html':
                # You may want to use a library like html2text to convert HTML to text
                return part.get_payload(decode=True).decode()
    else:
        # Not a multipart message, return the payload directly
        return msg.get_payload(decode=True).decode()