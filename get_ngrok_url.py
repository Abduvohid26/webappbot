import requests
from dotenv import load_dotenv, set_key
from pathlib import Path

# .env fayllari joylashgan manzillar
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATHS = [BASE_DIR / ".env", Path(__file__).parent / ".env"]
NGROK_URL_FILE = BASE_DIR / "ngrok_url.txt"  # Fayl bazaviy papkada saqlanadi

# .env fayllarini yuklash
for env_path in ENV_PATHS:
    load_dotenv(env_path)

def get_ngrok_url():
    """Ngrok tunneling URL'ini olish"""
    try:
        response = requests.get("http://ngrok:4040/api/tunnels")
        response.raise_for_status() 
        data = response.json()

        if "tunnels" in data and data["tunnels"]:
            ngrok_url = data["tunnels"][0]["public_url"]
            print(f"✅ Ngrok URL topildi: {ngrok_url}")
            return ngrok_url
        else:
            print("🚨 Ngrok tunnel mavjud emas!")
            return None
    except Exception as e:
        print(f"❌ Ngrok URL olishda xatolik: {e}")
        return None

if __name__ == "__main__":
    ngrok_url = get_ngrok_url()
    
    if ngrok_url:
        # ✅ Faylga yozish
        try:
            with open(NGROK_URL_FILE, "w") as f:
                f.write(ngrok_url)
            print(f"✅ {NGROK_URL_FILE} fayliga yozildi: {ngrok_url}")
        except Exception as e:
            print(f"❌ Faylga yozishda xatolik: {e}")

        # ✅ .env faylini yangilash
        for env_path in ENV_PATHS:
            set_key(str(env_path), "NGROK_URL", ngrok_url)
            print(f"✅ {env_path} faylida NGROK_URL yangilandi.")
    else:
        print("❌ Ngrok URL topilmadi.")
