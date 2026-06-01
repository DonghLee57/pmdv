# coding: utf-8
# Build helper to compile viewer.py into a standalone executable.
# units: s

import os
import subprocess
import sys

def ensure_icon():
    png_path = "icon.png"
    ico_path = "icon.ico"
    
    if not os.path.exists(png_path):
        possible_png = os.path.join("pmdv", "icon.png")
        if os.path.exists(possible_png):
            png_path = possible_png
            ico_path = os.path.join("pmdv", "icon.ico")
            
    if os.path.exists(png_path):
        if not os.path.exists(ico_path):
            print("Converting icon.png to icon.ico...")
            try:
                from PIL import Image
            except ImportError:
                print("Pillow not found. Installing pillow dependency...")
                subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True)
                from PIL import Image
            
            img = Image.open(png_path)
            img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"Icon converted and saved to {ico_path}")
        return ico_path, png_path
    else:
        print("Warning: icon.png not found. Executable will not have custom icon metadata.")
        return None, None

def main():
    print("=== PMDV Markdown Viewer Build System ===")
    
    if not os.path.exists(os.path.join("pmdv", "viewer.py")):
        print("Error: viewer.py not found. Running downloader.py first...")
        subprocess.run([sys.executable, "downloader.py"], check=True)
        
    try:
        import PyInstaller
        print(f"PyInstaller version {PyInstaller.__version__} detected.")
    except ImportError:
        print("PyInstaller is not installed in the current environment.")
        print("Installing build-time dependencies from requirements.txt...")
        pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        print(f"Running: {' '.join(pip_cmd)}")
        subprocess.run(pip_cmd, check=True)

    print("Checking and converting app icon assets...")
    ico_path, png_path = ensure_icon()

    print("Compiling viewer.py into a standalone executable...")
    # Use python -m PyInstaller to avoid PATH lookup issues on Windows
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--onefile",
        "--name=mdviewer"
    ]
    
    if ico_path and os.path.exists(ico_path):
        pyinstaller_cmd.append(f"--icon={ico_path}")
        
    if png_path and os.path.exists(png_path):
        sep = ";" if sys.platform.startswith("win") else ":"
        pyinstaller_cmd.append(f"--add-data={png_path}{sep}.")
        
    pyinstaller_cmd.append(os.path.join("pmdv", "viewer.py"))
    
    print(f"Running: {' '.join(pyinstaller_cmd)}")
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("\n===========================================================")
        print(" Build Completed Successfully!")
        print(" The executable can be found in the './dist/' folder:")
        if sys.platform.startswith("win"):
            print(" -> ./dist/mdviewer.exe")
        else:
            print(" -> ./dist/mdviewer")
        print("===========================================================")
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller build failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
