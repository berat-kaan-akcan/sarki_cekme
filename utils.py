import re
import os

def get_raw_headers(filepath="headers.txt"):
    """
    Reads the headers file. If it contains a curl command, it parses the headers out.
    Otherwise, it returns the raw text.
    """
    if not os.path.exists(filepath):
        return ""
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Eğer dosya bir curl komutu içeriyorsa
    if content.strip().startswith("curl"):
        headers = []
        for line in content.splitlines():
            line = line.strip()
            
            # -H veya --header ile başlayanlar
            if line.startswith("-H") or line.startswith("--header"):
                # CMD style curl (^" ... "^)
                match = re.search(r'\^"(.*?)"\^?', line)
                if match:
                    val = match.group(1)
                    val = val.replace('^%^', '%').replace('^&', '&').replace('^\\^"', '"')
                    headers.append(val)
                    continue
                    
                # Bash style or normal quotes ("..." or '...')
                match = re.search(r'["\'](.*?)["\']', line)
                if match:
                    headers.append(match.group(1))
                    
            # -b veya --cookie ile başlayanlar
            elif line.startswith("-b") or line.startswith("--cookie"):
                # CMD style
                match = re.search(r'\^"(.*?)"\^?', line)
                if match:
                    val = match.group(1)
                    val = val.replace('^%^', '%').replace('^&', '&')
                    headers.append("cookie: " + val)
                    continue
                    
                # Bash style
                match = re.search(r'["\'](.*?)["\']', line)
                if match:
                    headers.append("cookie: " + match.group(1))
                    
        if headers:
            return "\n".join(headers)
            
    # Curl komutu değilse, direkt olarak okunan metni (raw) döndür
    return content
