# LinkedInBot - Enhanced Profile Logger
Increase your likelihood to grow your connections and potentially get interview opportunities on LinkedIn by increasing visibility of your profile by viewing others profiles.

## About
When you view user's profile in LinkedIn they get notified that you have looked at their profile. This enhanced bot will automatically visit profiles from your LinkedIn home feed, extract profile data, and log everything with timestamps for analysis.

## ✨ New Enhanced Features

### 🔍 **Smart Profile Data Extraction**
- **Automatic data collection** from each visited profile
- **Configurable output fields**: URL, name, connection degree, country, email, phone
- **Timestamp logging** for every profile visit
- **CSV export** to `profile_data/profiles.csv`

### 🛡️ **Robust Error Handling**
- **Error logging** to `errorLog.csv` with timestamps
- **Graceful shutdown** with `Ctrl+C` signal handling
- **Automatic retry** with exponential backoff
- **Clean terminal output** (no Chrome error spam)

### 🧠 **Intelligent Stuck Detection**
- **Smart stuck detection** monitors for inactivity
- **Progressive recovery** strategy:
  1. Aggressive scrolling
  2. Page refresh
  3. Navigate to My Network and back
- **Auto-restart** when no new profiles found

### ⚡ **Performance Enhancements**
- **Infinite scrolling** on LinkedIn home feed
- **Skip own profile** automatically
- **Configurable max profiles** (default: 1000)
- **Random delays** (2-3 seconds per profile)

## Requirements
**Important:** make sure that you have your [Profile Viewing Setting](https://www.linkedin.com/settings/?trk=nav_account_sub_nav_settings) changed from 'Anonymous' to 'Public' so LinkedIn members can see that you have visited them and can visit your profile in return.
You also must change your language setting to **English**.

LinkedInBot was developed under [Python 3.8+](https://www.python.org/downloads).

Before you can run the bot, you will need to install a few Python dependencies. Run `pip3 install -r requirements.txt` to install them.

## Configuration
Create a `.env` file with your configuration:

```python
# Required Login
EMAIL = 'youremail@gmail.com'
PASSWORD = 'password'

# Output Configuration
OUTPUT_FIELDS = 'url,name,connection_degree,country,email,phone,timestamp'
MAX_PROFILE_VIEWS = 1000

# Legacy Settings (optional)
VIEW_SPECIFIC_USERS = False
SPECIFIC_USERS_TO_VIEW = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE = 5
CONNECT_WITH_USERS = True
RANDOMIZE_CONNECTING_WITH_USERS = True
JOBS_TO_CONNECT_WITH = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
ENDORSE_CONNECTIONS = False
RANDOMIZE_ENDORSING_CONNECTIONS = True
VERBOSE = True
```

## Quick Start
1. **Install dependencies**: `pip install -r requirements.txt`
2. **Create `.env` file** with your LinkedIn credentials
3. **Run the bot**: `python LinkedInBot.py`
4. **Choose browser** (Chrome recommended)
5. **Monitor progress** in terminal and check `profile_data/profiles.csv`

## Output Files

### 📊 **profiles.csv**
Contains extracted data for each visited profile:
- `url`: Full LinkedIn profile URL
- `name`: Profile name (if available)
- `connection_degree`: 1st, 2nd, 3rd connections
- `country`: Location information
- `email`: Email (N/A for most profiles)
- `phone`: Phone (N/A for most profiles)
- `timestamp`: ISO format timestamp of visit

### 📝 **errorLog.csv**
Logs all errors with timestamps for debugging.

## Features

### 🎯 **Smart Profile Visiting**
- Visits profiles from LinkedIn home feed
- Skips your own profile automatically
- Random 2-3 second delays between visits
- Returns to feed after each profile visit

### 🔄 **Auto-Recovery**
- Detects when stuck (no new profiles in 2+ minutes)
- Implements progressive recovery strategies
- Handles LinkedIn rate limiting gracefully

### 🛑 **Graceful Shutdown**
- Press `Ctrl+C` to stop safely
- Saves all progress before exiting
- Prints summary of visited profiles

## POTENTIAL ISSUES

* **2 Factor Authentication**
  * Solution: Enter the code when prompted (not compatible with headless mode)
* **LinkedIn Security Email**
  * Enter the PIN if prompted, or restart the bot
  * Consider reducing activity if flagged
* **No profiles found**
  * The bot will automatically implement recovery strategies
  * Check `errorLog.csv` for specific issues

## DISCLAIMER

The use of bots and scrapers are mentioned [here](https://www.linkedin.com/help/linkedin/answer/56347/prohibited-software-and-extensions?lang=en).
Use this bot at your own risk. 
Just to push more knowledge a judge in California ruled that they cannot prohibit bots([article](https://www.bbc.com/news/technology-40932487)).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Attribution

This project is inspired by [helloitsim's LInBot](https://github.com/helloitsim/LInBot) project.
Significant improvements and new features by [hamiltoncjames](https://github.com/hamiltoncjames).

This enhanced version includes:
- Profile data extraction and logging
- Smart stuck detection and recovery
- Graceful shutdown handling
- Error logging and suppression
- Timestamp tracking
- Infinite scrolling optimization
