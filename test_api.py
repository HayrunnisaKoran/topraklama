"""API'yi test etmek için basit script"""
import sys
import traceback

try:
    print("App.py import ediliyor...")
    from app import app, initialize_system
    
    print("Sistem baslatiliyor...")
    initialize_system()
    
    print("API baslatiliyor...")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    
except Exception as e:
    print(f"HATA: {e}")
    traceback.print_exc()
    sys.exit(1)

