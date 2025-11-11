"""
Script to automatically download and install FFmpeg on Windows
"""
import os
import sys
import urllib.request
import zipfile
import shutil

def download_ffmpeg():
    print('=' * 60)
    print('FFMPEG INSTALLER FOR WINDOWS')
    print('=' * 60)
    
    # FFmpeg URL for Windows (static build)
    ffmpeg_url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
    
    print('\n📥 Downloading FFmpeg...')
    print('This may take a few minutes depending on your connection...')
    
    try:
        # Download FFmpeg
        zip_path = 'ffmpeg.zip'
        urllib.request.urlretrieve(ffmpeg_url, zip_path, reporthook=download_progress)
        
        print('\n\n📦 Extracting files...')
        
        # Extract the file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Find extracted folder
        folders = [f for f in os.listdir('.') if f.startswith('ffmpeg-') and os.path.isdir(f)]
        if folders:
            ffmpeg_folder = folders[0]
            
            # Move ffmpeg.exe to current folder
            ffmpeg_exe = os.path.join(ffmpeg_folder, 'bin', 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                shutil.copy(ffmpeg_exe, 'ffmpeg.exe')
                print(f'✅ FFmpeg installed successfully at: {os.path.abspath("ffmpeg.exe")}')
                
                # Clean up temporary files
                print('\n🧹 Cleaning up temporary files...')
                os.remove(zip_path)
                shutil.rmtree(ffmpeg_folder)
                
                print('\n' + '=' * 60)
                print('✅ INSTALLATION COMPLETED')
                print('=' * 60)
                print('\nYou can now run the bot with: python bot.py')
                return True
        
        print('❌ Error: Could not find ffmpeg.exe in downloaded file')
        return False
        
    except Exception as e:
        print(f'\n❌ Error during installation: {e}')
        print('\nPlease install FFmpeg manually:')
        print('1. Go to: https://ffmpeg.org/download.html')
        print('2. Download the Windows version')
        print('3. Extract and add the bin folder to PATH')
        return False

def download_progress(block, block_size, total_size):
    """Show download progress"""
    downloaded = block * block_size
    percentage = min(100, (downloaded / total_size) * 100)
    bar = '█' * int(percentage / 2) + '░' * (50 - int(percentage / 2))
    print(f'\r[{bar}] {percentage:.1f}%', end='', flush=True)

if __name__ == '__main__':
    print('\n⚠️  NOTE: This download is approximately 80MB\n')
    response = input('Do you want to continue? (y/n): ')
    
    if response.lower() in ['y', 'yes']:
        download_ffmpeg()
    else:
        print('\nInstallation cancelled.')
        print('\nTo install FFmpeg manually:')
        print('1. Go to: https://ffmpeg.org/download.html')
        print('2. Download the Windows version')
        print('3. Extract and add to system PATH')
