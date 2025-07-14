import sys
import os
import re
from gazpacho import get, Soup 

url = sys.argv[1]
html = get(url)
soup = Soup(html)

description = soup.find("meta", {"property": "og:description"}).attrs['content'].split('-', 1)[1].strip()
description = re.sub(r'[\n]+', '\n', description)

title = soup.find("meta", {"property": "og:title"}).attrs['content']
title = title.split('-')[0].strip()

if not os.path.exists(title):
    os.makedirs(f"{title}/src/")

with open(f"{title}/question", "w") as f:
    f.write(description)
