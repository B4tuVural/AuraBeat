#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# .env.example oku
if __name__ == "__main__":
    with open(".env.example", "r") as f:
        content = f.read()

    # Credential'ları istemek
    gemini = input("GEMINI_API_KEY (ZORUNLU): ").strip()
    spotify_id = input("SPOTIFY_CLIENT_ID (opsiyonel, önerilir): ").strip()
    spotify_secret = input("SPOTIFY_CLIENT_SECRET (opsiyonel, önerilir): ").strip()

    # Değerleri değiştir
    content = content.replace("GEMINI_API_KEY=your-gemini-api-key-here", f"GEMINI_API_KEY={gemini}")
    content = content.replace("SPOTIFY_CLIENT_ID=", f"SPOTIFY_CLIENT_ID={spotify_id}")
    content = content.replace("SPOTIFY_CLIENT_SECRET=", f"SPOTIFY_CLIENT_SECRET={spotify_secret}")

    # .env dosyasını oluştur
    with open(".env", "w") as f:
        f.write(content)

    print("✅ .env dosyası oluşturuldu!")