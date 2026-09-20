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
- [x] Day 27 - Multilingual UI & Premium Now Playing

### 🌍 Multilingual Experience
- Added centralized `LanguageManager`
- Added reusable global `UITranslator`
- Added live runtime language switching
- Added English language support
- Added Hindi (हिन्दी) language support
- Added French (Français) language support
- Language preference persists between sessions
- Major LYRx screens now update without restarting the application
- Song titles, artist names, user content, and provider metadata remain unchanged

### 🎧 Premium Now Playing Experience
- Redesigned Now Playing panel with a premium LYRx visual style
- Added custom vector-based playback controls
- Added dynamic Play / Pause button states
- Added polished Previous and Next controls
- Added functional Shuffle and Repeat active states
- Added purple neon Play/Pause glow
- Added playback-aware animated mini equalizer
- Equalizer and glow animation react to actual playback state
- Improved album artwork presentation and purple glow
- Improved seek/progress and volume controls
- Added dynamic volume percentage
- Improved Next Up queue presentation
- Added online/local audio status presentation
- Added live English, Hindi, and French translations to Now Playing

### 🎵 Future Playback Actions
The Now Playing interface also includes UI foundations for:
- Add to Queue
- Add to Playlist
- Share
- More track actions

These actions are intentionally reserved for deeper application/provider integration before the commercial release.

- [x] Day 28 - LYRx Kids Mode

LYRx now includes a dedicated Kids Mode designed as a separate,
child-friendly experience inside the same desktop application.

### ✨ Kids Mode Features

- Dedicated Kids Mode home experience
- Separate child-friendly sidebar and navigation
- Custom LYRx Kids visual identity and hero experience
- Kids-only content discovery
- Kids Music
- Audible Stories
- Poems & Rhymes
- Spiritual content
- Persistent Kids Favorites
- Search inside Kids content sections
- Dedicated Kids mini/floating player
- Main LYRx player isolated from Kids Mode
- Kids-specific playback experience
- Popular for Kids discovery shortcuts

### 🎓 Study & Learn

Kids Mode also introduces an interactive learning area with:

- English Alphabets
- Numbers from 1–100
- Visual tens & ones number learning
- Hindi वर्णमाला
- French Alphabet
- Colors & Shapes
- Interactive Kids Math
- Addition
- Subtraction
- Multiplication
- Division

Study & Learn uses category-based navigation so children can explore
one learning activity at a time without overcrowding the interface.

### 🛡️ Parental Controls & Kids Safety

- Dedicated Kids Settings
- Safe Search controls
- Explicit-content filtering
- Harmful-content filtering
- Persistent parental preferences
- Parent Exit PIN protection
- Separate Kids Mode environment
- Child-focused discovery filtering

### 🎨 Kids UX

- Dedicated Kids Mode theme
- Child-friendly typography and spacing
- Custom Kids banner artwork
- LYRx Kids navigation icon
- Larger visual learning elements
- Dedicated window controls
- Responsive scrollable learning grids
- Separate Kids Mode navigation from the main LYRx interface

> Kids Mode is being built around a simple principle:
> **Listen • Learn • Imagine**

- [x] Day 29 - Final UX, Local Library, Playlists, Favorites, AI Actions & Splash Experience

### 🎛️ Home & Discovery Experience

- Made **Your Vibe** mood shortcuts functional
- Added expandable mood discovery with additional moods
- Connected mood selections to the real Discover search flow
- Made **Playlists for You** cards open real playlists
- Made Home playlist navigation and View All actions functional
- Refined the LYRx sidebar logo/symbol sizing

### 💿 Local Music Library

- Added **Add Local Music** workflow for desktop audio files
- Supports importing multiple local audio files
- Persists imported local-library paths between sessions
- Rebuilds local metadata when the application starts
- Added local metadata extraction using Mutagen
- Reads title, artist, album and duration where metadata is available
- Supports embedded artwork from MP3/ID3, FLAC and M4A/MP4 sources
- Added a dedicated **LYRx LOCAL** artwork fallback when a local file has no embedded cover
- Local tracks use their own artwork and never fall back to unrelated demo-song artwork
- Added real local-track duration display
- Local tracks play through the real LYRx Now Playing pipeline
- Local artwork is synchronized with the main player and floating player
- Preserved offline/local playback behavior without requiring an online provider

### ❤️ Favorites & Playlists

- Improved Favorites layout into a structured multi-column grid
- Added functional playlist creation and persistence
- Added playlist opening and playlist-specific playback
- Added online songs to playlists from the playback/discovery workflow
- Added playlist queue/Next Up integration
- Added playlist song removal controls
- Added playlist artwork handling and dynamic artwork propagation
- Added modern LYRx-styled confirmation/notification UI for playlist actions
- Improved playlist song playback so online playlist tracks use their actual playable source rather than artwork/cache paths

### 🤖 LYRx AI Assistant — App Actions

LYRx AI was extended beyond conversational music discovery into application-aware actions.

The assistant can now work with LYRx's existing music state for tasks such as:

- Discovering and playing music through the existing provider pipeline
- Working with the user's Favorites collection
- Creating/working with playlists through LYRx's playlist system
- Playing a requested track from the user's saved music context where a playable track is available
- Connecting AI requests to real application actions instead of presenting only text responses

The AI action layer is intentionally built around LYRx's existing providers, player, Favorites and Playlist stores so that unsupported actions are not presented as completed when they are not actually available.

### 🎚️ Quick Actions & Playback Integration

- Improved Now Playing action integration
- Connected queue/playlist/share action foundations with the real player state where supported
- Preserved provider-aware online playback and local offline playback
- Improved online queue handling and Next Up synchronization
- Fixed playlist queue data-shape compatibility between Playlist and Now Playing layers
- Fixed online queue objects so Next Up can render provider-backed song metadata safely

### 🎬 LYRx Cinematic Splash Experience

Day 29 also introduced a branded startup experience inspired by modern streaming applications.

- Added LYRx intro video splash screen
- Added dedicated opening LYRx artwork
- Added dedicated closing LYRx artwork
- Preserved the original purple LYRx visual identity of the intro video
- Added a smooth transition from the intro experience into the main application
- Removed the need for a manual Skip button for the current release build
- Fixed splash rendering issues that could cause black-screen pauses
- Fixed painter/rendering errors in the splash layer
- Kept the main application launch flow intact after the cinematic intro

### 🧪 Day 29 QA / Stability

- Tested Home mood navigation
- Tested playlist creation/opening/playback
- Tested online playlist tracks and queue behavior
- Tested Favorites integration
- Tested local music import and playback
- Tested local metadata/artwork handling
- Tested Now Playing artwork synchronization
- Tested LYRx AI music actions
- Tested Kids Mode regression after major playback changes
- Tested startup splash and main-window transition
- Fixed multiple queue/data-model compatibility issues discovered during integration testing

> Day 29 goal: move LYRx from a feature-complete prototype toward a coherent, testable alpha release where the major user flows connect to real application state instead of isolated demo UI.

Version: LYRx Alpha 1.0