# Autofill Zeitman
Filling out Zeitman is boring. This script might make some of the pain go away.

# Installation
The required packages can be installed with `pip install -r requirements.txt`.

The script has been tested with Python 3.9.

# Usage
1. Rename or copy `config_template.py` to `config.py`
2. Edit `config.py` with the desired information
3. Run the script with `python zeitman_auto.py`

Script autofills working hours based on some average start and end times plus some user-defined random noise.

Weekends and holidays are ignored, but currently all working hours are set to "present". No teleworking option yet.

Warning: it will only work if your Zeitman language is set to English. And even then I make no promises.

# Contributions
Anyone is more than welcome to make it better.
Please open an issue for any problems or suggestions.
