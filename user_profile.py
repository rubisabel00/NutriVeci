import json
import os
from typing import Dict, List

class UserProfile:
    def __init__(self):
        self.profiles_file = 'data/user_profiles.json'
        self._ensure_profiles_file_exists()
    
    def _ensure_profiles_file_exists(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def save_profile(self, user_id: int, data: Dict) -> bool:
        try:
            profiles = self._load_profiles()
            profiles[str(user_id)] = data
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar perfil: {str(e)}")
            return False

    def get_profile(self, user_id: int) -> Dict:
        profiles = self._load_profiles()
        return profiles.get(str(user_id), {})

    def _load_profiles(self) -> Dict:
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}