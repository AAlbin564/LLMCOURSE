import subprocess
import time
import os

input_file = "links.txt"
output_dir = "rawHTML"
with open(input_file,"r") as f:
    for url in f:
        url = url.strip()
        time.sleep(4)
        if url:
            filename = url.replace("://", "_").replace("/", "_").replace("?", "_").replace("https", "").replace("www.uu.se","")
            output_path = os.path.join(output_dir, f"{filename}.html")
            subprocess.run(["curl", url, "-o", output_path])
