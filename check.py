import requests

# Proxy sozlamalari
proxy = {
    "http": "http://ytcheck:ytcheck@23.142.16.81:65199",
    "https": "http://ytcheck:ytcheck@23.142.16.81:65199",
}

video_url = input("YouTube video URL ni kiriting: ")

try:
    response = requests.get(video_url, proxies=proxy, timeout=10)
    if response.status_code == 200:
        print("✅ Proxy ishlayapti! YouTube sahifasi yuklandi.")
    else:
        print(f"❌ Xatolik! HTTP Status Code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ Proxy ishlamayapti yoki bloklangan! Xatolik: {e}")
