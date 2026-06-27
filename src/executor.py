import os
import subprocess
import webbrowser
from .logger import logger

class CommandExecutor:
    @staticmethod
    def open_browser_search(params):
        query = params.get("query", "")
        url = f"https://www.youtube.com/results?search_query={query}" if "youtube" in query.lower() else f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching for '{query}' in browser."

    @staticmethod
    def system_sleep(params):
        # Windows: rundll32.exe powrprof.dll,SetSuspendState 0,1,0
        # Linux: systemctl suspend
        if os.name == 'nt':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("systemctl suspend")
        return "Putting the laptop to sleep."

    @staticmethod
    def system_shutdown(params):
        # Windows: shutdown /s /t 1
        # Linux: shutdown -h now
        if os.name == 'nt':
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown -h now")
        return "Shutting down the laptop."

    @staticmethod
    def lock_screen(params):
        # Windows: rundll32.exe user32.dll,LockWorkStation
        # Linux: xdg-screensaver lock (depends on DE)
        if os.name == 'nt':
            os.system("rundll32.exe user32.dll,LockWorkStation")
        else:
            os.system("xdg-screensaver lock")
        return "Locking the screen."

    @staticmethod
    def open_app(params):
        app_name = params.get("app_name", "")
        # This is a basic implementation; Windows might need full paths or start command
        if os.name == 'nt':
            os.system(f"start {app_name}")
        else:
            os.system(f"{app_name} &")
        return f"Opening application: {app_name}"

    @staticmethod
    def close_app(params):
        app_name = params.get("app_name", "")
        # Windows: taskkill /F /IM app.exe
        # Linux: pkill app
        if os.name == 'nt':
            os.system(f"taskkill /F /IM {app_name}.exe")
        else:
            os.system(f"pkill {app_name}")
        return f"Closing application: {app_name}"

    @classmethod
    def execute(cls, action, params):
        handlers = {
            "open_browser_search": cls.open_browser_search,
            "system_sleep": cls.system_sleep,
            "system_shutdown": cls.system_shutdown,
            "lock_screen": cls.lock_screen,
            "open_app": cls.open_app,
            "close_app": cls.close_app,
        }
        
        handler = handlers.get(action)
        if handler:
            try:
                result = handler(params)
                logger.info(f"Executed action '{action}' with result: {result}")
                return result
            except Exception as e:
                error_msg = f"Failed to execute '{action}': {str(e)}"
                logger.error(error_msg)
                return error_msg
        else:
            return f"Unknown action: {action}"
