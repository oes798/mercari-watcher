import os
import requests
import imagehash
from PIL import Image
from io import BytesIO
from discord_webhook import DiscordWebhook

KEYWORD = "アバクロ"
WEBHOOK_URL = "https://discord.com/api/webhooks/1395315477638680736/1dZqFYRAvC_6s-S8pNgaKamQGivEy8pPD9NzXaxKGBI7gTTE90DQnhunZb3zPHSeZPNW"
IMAGE_FOLDER = "reference_images"
SIMILARITY_THRESHOLD = 5

def fetch_mercari_results(keyword):
    search_url = f"https://www.mercari.com/jp/search/?keyword={{keyword}}"
    headers = {
    "User-Agent": "Mozilla/5.0"
}
    resp = requests.get(search_url, headers=headers)
    return resp.text

def download_image(url):
    try:
        resp = requests.get(url)
        return Image.open(BytesIO(resp.content))
    except:
        return None

def is_similar(img1, img2):
    try:
        hash1 = imagehash.phash(img1)
        hash2 = imagehash.phash(img2)
        return abs(hash1 - hash2) <= SIMILARITY_THRESHOLD
    except:
        return False

def send_alert(image_url, title):
    content = f"🔔 **Possible Match Found**: {{title}}\n{{image_url}}"
    DiscordWebhook(url=WEBHOOK_URL, content=content).execute()

def check_new_items():
    html = fetch_mercari_results(KEYWORD)
    dummy_items = [
        {{
            "title": "アバクロのニットテスト",
            "image": "https://static.mercdn.net/item/detail/orig/photos/m123456.jpg"
        }}
    ]
    ref_images = [Image.open(os.path.join(IMAGE_FOLDER, f)) for f in os.listdir(IMAGE_FOLDER)]
    for item in dummy_items:
        target_img = download_image(item["image"])
        if not target_img:
            continue
        for ref in ref_images:
            if is_similar(ref, target_img):
                send_alert(item["image"], item["title"])
                break

if __name__ == "__main__":
    check_new_items()
