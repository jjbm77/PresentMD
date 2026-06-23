import os
from pathlib import Path

class ThemeManager:
    def __init__(self, internal_dir: Path):
        self.internal_dir = internal_dir
        self.user_dir = self._get_user_theme_dir()
        
    def _get_user_theme_dir(self) -> Path:
        if os.name == 'nt':
            appdata = os.environ.get('APPDATA', '~')
            return Path(appdata) / 'presentmd' / 'themes'
        else:
            return Path.home() / '.config' / 'presentmd' / 'themes'
            
    def get_theme_css(self, theme_name: str) -> str:
        """Retrieves the CSS for the requested theme.
        Checks user directory first, then internal directory, then falls back to default.
        """
        # Alias/fallback for renamed themes
        if theme_name == "nexus-minimal":
            theme_name = "minimal"

        # 1. Check user directory: ~/.config/presentmd/themes/<theme_name>/styles.css
        user_theme_dir = self.user_dir / theme_name
        user_css_file = user_theme_dir / "styles.css"
        if user_css_file.exists():
            return user_css_file.read_text(encoding="utf-8")
            
        # 2. Check internal directory: templates/themes/<theme_name>/styles.css
        internal_css_file = self.internal_dir / theme_name / "styles.css"
        if internal_css_file.exists():
            return internal_css_file.read_text(encoding="utf-8")
            
        # 3. Fallback
        fallback = self.internal_dir / "nexus-blueprint" / "styles.css"
        if fallback.exists():
            return fallback.read_text(encoding="utf-8")
            
        return ""
