<p align="center">
<img src="assets/icons/logo/LYRx_symbol.png" width="170">
</p>

<h1 align="center">
<img src="assets/icons/logo/LYRx_wordmark.png" width="170">
</h1>

<p align="center">
A futuristic offline desktop music player built with Python & PySide6.
</p>


# LYRx

LYRx is a modern offline desktop music player built with Python.

Unlike traditional music players, LYRx focuses on a premium user experience with beautiful animations, mood-based music discovery, and a clean modern interface.

---

## Features (Planned)

- Modern UI
- Floating Mini Player
- Album Art Support
- Mood-based Music
- Smart Library
- Lyrics
- Favorites
- Playlists
- Dynamic Themes
- Beautiful Animations

---

## Tech Stack

- Python
- PySide6
- Qt Designer
- Mutagen
- Pillow

---

## Status

🚧 Currently in Development

## Development Progress

- [x] Day 1 - Project Setup
- [x] Day 2 - Git & GitHub
- [x] Day 3 - PySide6 Basics
- [x] Day 4 - Window Foundation
- [x] Day 5 - Hero Banner & Music Cards
- [x] Day 6 - HomeScreen Architecture
- [x] Day 7 - Sidebar & Navigation UI
- [x] Day 8 - Main UI Components & Visual Enhancement
- [x] Day 9 - HomeScreen & Now Playing UI Polish
- [x] Day 10 - Premium Hero Banner, Mood Section & Music UI Enhancement
- [x] Day 11 - Complete automatic next-song playback
- [x] Day 12 - Implemented shuffle and repeat playback controls
- [x] Day 13 - (a) Upgraded MusicCard UI and interaction experience
             - (b) Implemented persistent Favorites functionality
             - (c) Improved song duration and metadata handling
             - (d) Refined music browsing and selection flow
- [x] Day 14 - Navigation & Floating Player Integration
- [x] Day 15 - Refine sidebar and make Library playable
- [x] Day 16 - Enabled Dark Mode Toggle Theme
- [x] Day 17 - Added Playlists feature into Sidebar Panel
- [x] Day 18 - LYRx AI Assistant Integration

Introduced the first functional AI assistant inside LYRx.

The AI Assistant is now integrated directly into the desktop music player instead of being only a visual demo.

### Features Completed

- Added dedicated **LYRx AI Assistant** screen
- Integrated AI Assistant with the main sidebar navigation
- Added responsive dark/light theme support
- Added conversational chat interface
- Added user and AI message bubbles
- Added quick music prompts
- Added **Clear Chat** functionality
- Added local music-aware recommendation logic
- Added mood-based music suggestions
- Added song discovery responses based on the current LYRx catalog

### AI Player Controls

LYRx AI can now understand player commands such as:

- `Play Believer`
- `Play Faded`
- `Pause song`
- `Resume song`
- `Stop song`
- `Next song`
- `Previous song`

These commands are connected to the actual LYRx audio player.

- [x] Day 19 — Online Music Streaming Integration

### Completed

- Added unified `Song` model for online tracks
- Added `MusicService`
- Integrated Jamendo online music catalog
- Added asynchronous online music loading in Discover
- Added online album artwork
- Added real online audio streaming
- Added online queue support
- Added online Next / Previous controls
- Added online Next Up queue
- Added online Next Up thumbnails
- Synced online songs with Now Playing
- Synced online songs with Floating Player
- Added floating player online artwork support
- Preserved local music playback compatibility
- Added online stream error handling and retry support

- [x] Day 20 -  Multi-Provider Online Music Search

### Completed

- Added unified multi-provider music architecture
- Added ProviderRegistry
- Integrated iTunes catalog provider
- Retained Jamendo provider as online playable fallback
- Added mainstream Hindi / Bollywood / English catalog discovery
- Added artist and song search support
- Added genre and mood-ready provider architecture
- Added online album artwork support
- Added online song playback pipeline
- Added provider-independent Song model
- Added preview/full playback capability detection

### Current Provider Support

- iTunes / Apple catalog:
  - Mainstream song discovery
  - Hindi / Bollywood / English music
  - Album artwork
  - Artist / album metadata
  - Preview playback
- Jamendo:
  - Independent online catalog
  - Full-track playback where available

- [x] Day 21 - YT BOX & Online Playback Improvements

### Added
- Dedicated YT BOX page for YouTube music/video discovery
- YouTube metadata search with dynamic result cards
- YouTube favorites with persistent local storage
- YouTube favorites integrated into the main Favorites page
- Add YouTube results to existing playlists
- Create a new playlist directly from the Add to Playlist dialog
- Modernized Add to Playlist popup UI
- Improved online queue handling for iTunes tracks
- Fixed iTunes Next Up direct-click playback
- Improved Next / Previous behavior for online songs

- [x] Day 22 - Finalize YT Box discovery and official playback fallback
- [x] Day 23 - Add Firebase authentication and Google sign-in
- [x] Day 24 - Firebase phone OTP authentication
- [x] Day 25 - Professional Settings & Personalization

### Implemented

- Category-based Settings dashboard with dedicated detail pages and back navigation
- Firebase-aware Profile & Account screen
- Editable first name, last name, date of birth, gender and profile photo
- Per-user local profile persistence using Firebase UID
- Change/remove profile photo with LYRx-styled confirmation dialogs
- Dark/light appearance controls with animated custom toggle switches
- Compact-layout preference persistence
- Playback preferences connected to the real player:
  - Autoplay
  - Gapless transition behavior
  - Crossfade-style fade transitions
  - Volume-normalization preference groundwork
- Audio/network preferences:
  - Streaming quality preference
  - Data Saver mode
  - Provider-aware source selection where supported
  - Reduced online artwork fetching in Data Saver mode
- Downloads & Storage groundwork:
  - Configurable download directory
  - Open download directory
  - Real cache directory
  - Cache-size reporting
  - Clear-cache action
- Privacy & Security:
  - Private listening preference
  - Firebase account-security shortcut
  - Privacy Policy link
- Notifications:
  - Music recommendation preference
  - Application update preference
  - Windows desktop test notification
- Language & Region:
  - English current UI
  - Persistent region preference
  - Internationalization-ready roadmap
- Accessibility:
  - Reduce Motion behavior
  - Larger Settings text
- About LYRx:
  - Version/build information
  - Technology information
  - Website, Privacy Policy and Terms links

- [x] Day 26 - Offline downloads foundation


Version: LYRx Alpha 1.0