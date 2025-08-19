# Gameloop Discord Rich Presence

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Automatically updates your Discord status when playing mobile games on Gameloop Android Emulator. Shows the current game, play time, and whether you're actively playing or idle.

## Features

- 🎮 **Auto-detection** - Automatically detects when Gameloop is running
- 📱 **Game Recognition** - Recognizes 10+ popular mobile games and apps
- ⏱️ **Play Time Tracking** - Shows how long you've been playing
- 💤 **Smart Idle Detection** - Detects when you're not actively using Gameloop
- 🔄 **Real-time Updates** - Updates Discord status in real-time
- 🛠️ **Auto-configuration** - Automatically finds Gameloop and ADB paths

## Screenshots

![Main GUI Interface](https://i.ibb.co/7JxRmh9c/image.png)
*Main application interface with status monitoring and controls*

![Discord Rich Presence Example](https://i.ibb.co/gbgJwG4C/image.png)
*Discord showing game status and play time*

![System Tray Integration](https://i.ibb.co/nMKMSRRj/image.png)
*Application running minimized in system tray*

## Supported Games & Apps

- Launcher UI
- Settings
- FX File Explorer
- Google Play Store
- Google Play Games
- WhatsApp
- Facebook
- Twitter
- YouTube
- PUBG Mobile
- Call of Duty Mobile
- Free Fire

## Prerequisites

- Windows 10/11
- Gameloop Android Emulator
- Discord Desktop App
- Python 3.7+ (for running from source)

## Installation

### Option 1: Download Executable (Recommended)

1. Download the latest release from [Releases](https://github.com/iMikano/gameloop-discord-rpc/releases)
2. Extract the ZIP file
3. Run `gameloop-discord-rpc.exe`

### Option 2: Run from Source

1. Clone this repository:
```bash
git clone https://github.com/iMikano/gameloop-discord-rpc.git
cd gameloop-discord-rpc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python Gameloop-Discord-RPC.py
```

## Setup Discord Application

To use this application, you need to set up a Discord application:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Copy the Application ID
4. Upload game icons to "Rich Presence → Art Assets":
   - `gameloop-logo` - Main Gameloop logo
   - `pubg_mobile`, `cod_mobile`, etc. - Game-specific icons
   - `android` - Default icon for unknown apps

## Usage

1. **Start Discord** - Make sure Discord desktop app is running
2. **Start the monitor** - Run the executable or Python script
3. **Launch Gameloop** - Open Gameloop and start playing
4. **Check Discord** - Your status should automatically update

The application will:
- Detect when Gameloop starts/stops
- Show the current game you're playing
- Track your play time
- Switch to "Idle" after 5 minutes of inactivity
- Update automatically when you switch games

## Configuration

### Custom Games

To add support for custom games, edit the `games` dictionary in the script:

```python
self.games = {
    'com.your.custom.game': {
        'name': 'Your Game Name',
        'icon': 'your_game_icon'
    }
}
```

### Settings

- **Update Interval**: Change `self.update_interval = 10` (seconds)
- **Idle Threshold**: Change `self.idle_threshold = 300` (seconds)
- **Discord Client ID**: Change `CLIENT_ID` in main function

## Troubleshooting

### "Failed to connect to Discord"
- Make sure Discord desktop app is running
- Restart Discord and try again

### "ADB not found" or "Device not found"
- Make sure Gameloop is fully loaded (not just starting)
- Make sure adb Debugging option is enabled from Gameloop settings
- Try restarting Gameloop
- The script auto-detects ADB from Gameloop installation

### Games not recognized
- Check if the game's package name is in the supported list
- Add custom games using the configuration method above

### Rich Presence not showing
- Make sure you've uploaded the required images to Discord Developer Portal
- Check that the image names match exactly (case-sensitive)

## Building from Source

To create an executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
- Execute build.bat

3. The executable will be in the `dist/` folder

## Dependencies

- `psutil` - Process monitoring
- `pypresence` - Discord Rich Presence
- `pywin32` - Windows API access
- `tkinter` - GUI framework
- `Pillow` - Image processing
- `pystray` - System tray integration
- `requests` - HTTP requests

## Contact

- **Discord**: @sp1_
- **GitHub**: [@iMikano](https://github.com/iMikano)
- **Instagram**: [@var.mikano](https://instagram.com/var.mikano)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Discord for the Rich Presence API
- Gameloop/TencentGameAssistant for the Android emulator

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/iMikano/gameloop-discord-rpc/issues) page
2. Create a new issue with detailed information
3. Include your OS version and error messages

---


⭐ If this project helps you, consider giving it a star!

