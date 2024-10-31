import os

browsers = {
    'Chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'Edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'Firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe'
}

def get_browser_path():    
    installed_browsers = [path for name, path in browsers.items() if os.path.exists(path)]

    if installed_browsers:
        return installed_browsers[0]
    else:
        return None


