# ============================================================
# LYRx
# DAY 21 - PHASE 1
#
# FILE 1
# spotify_provider.py
#
# PURPOSE:
#   Spotify authenticated catalog + full playback control
#
# IMPORTANT:
#   Spotify does NOT give LYRx a direct MP3 URL.
#
#   Full songs are played through the user's authorized
#   Spotify playback device / Spotify Connect session.
#
#   Architecture:
#
#       LYRx UI
#          |
#          v
#       SpotifyProvider
#          |
#          +---- Search catalog
#          |
#          +---- Start / pause playback
#          |
#          +---- Next / previous
#          |
#          +---- Seek
#          |
#          +---- Volume
#          |
#          +---- Current playback
#
#   Existing Jamendo and iTunes providers remain untouched.
# ============================================================

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import time
import webbrowser

from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)

from pathlib import Path

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from urllib.parse import (
    parse_qs,
    urlencode,
    urlparse,
)

import requests

from dotenv import load_dotenv

from services.music_provider import (
    MusicProvider,
    MusicSearchResult,
    Song,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(
    __file__
).resolve()

SRC_DIR = FILE_DIR.parents[1]

PROJECT_DIR = FILE_DIR.parents[2]

TOKEN_DIR = (
    PROJECT_DIR
    / ".lyrx"
)

TOKEN_FILE = (
    TOKEN_DIR
    / "spotify_token.json"
)


# ============================================================
# CALLBACK HANDLER
# ============================================================

class SpotifyCallbackHandler(
    BaseHTTPRequestHandler
):

    """
    Tiny local OAuth callback server.

    Spotify redirects the browser here after the user
    approves LYRx access.
    """

    auth_code = ""

    auth_state = ""

    auth_error = ""

    # ========================================================
    # GET
    # ========================================================

    def do_GET(
        self
    ):

        parsed = urlparse(
            self.path
        )

        params = parse_qs(
            parsed.query
        )

        # ----------------------------------------------------
        # AUTH CODE
        # ----------------------------------------------------

        SpotifyCallbackHandler.auth_code = (

            params.get(
                "code",
                [""]
            )[0]

            or ""

        )

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        SpotifyCallbackHandler.auth_state = (

            params.get(
                "state",
                [""]
            )[0]

            or ""

        )

        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        SpotifyCallbackHandler.auth_error = (

            params.get(
                "error",
                [""]
            )[0]

            or ""

        )

        # ====================================================
        # BROWSER RESPONSE
        # ====================================================

        if SpotifyCallbackHandler.auth_code:

            title = (
                "LYRx Spotify Connected"
            )

            message = (
                "Spotify authorization successful."
                "<br><br>"
                "You can close this browser tab "
                "and return to LYRx."
            )

        else:

            title = (
                "LYRx Spotify Authorization"
            )

            message = (
                "Spotify authorization was not completed."
                "<br><br>"
                "Return to LYRx and try again."
            )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>

            <style>
                body {{
                    margin: 0;
                    background: #0B0913;
                    color: white;
                    font-family: Arial, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }}

                .card {{
                    width: 480px;
                    padding: 40px;
                    background: #171125;
                    border: 1px solid #55358A;
                    border-radius: 22px;
                    text-align: center;
                    box-shadow:
                        0 20px 60px rgba(
                            0,
                            0,
                            0,
                            0.35
                        );
                }}

                h1 {{
                    color: #A970FF;
                }}

                p {{
                    color: #C7BCE0;
                    line-height: 1.6;
                }}

                .logo {{
                    font-size: 46px;
                    margin-bottom: 12px;
                }}
            </style>
        </head>

        <body>

            <div class="card">

                <div class="logo">
                    ♪
                </div>

                <h1>
                    {title}
                </h1>

                <p>
                    {message}
                </p>

            </div>

        </body>
        </html>
        """

        body = html.encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(
                len(body)
            )
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    # ========================================================
    # SILENCE SERVER LOG
    # ========================================================

    def log_message(
        self,
        format,
        *args
    ):

        return


# ============================================================
# SPOTIFY PROVIDER
# ============================================================

class SpotifyProvider(
    MusicProvider
):

    # ========================================================
    # IDENTITY
    # ========================================================

    provider_name = (
        "spotify"
    )

    display_name = (
        "Spotify"
    )

    # ========================================================
    # CAPABILITIES
    # ========================================================

    supports_search = True

    supports_trending = False

    supports_popular = False

    supports_genres = True

    supports_moods = True

    supports_hindi = True

    supports_english = True

    supports_artist_search = True

    supports_song_search = True

    supports_charts = False

    # --------------------------------------------------------
    # Spotify supports full playback CONTROL through an
    # authorized Spotify playback device.
    #
    # It does NOT provide direct MP3 URLs.
    # --------------------------------------------------------

    supports_full_playback = True

    supports_preview = False

    supports_download = False

    # ========================================================
    # ENDPOINTS
    # ========================================================

    API_BASE_URL = (
        "https://api.spotify.com/v1"
    )

    AUTH_URL = (
        "https://accounts.spotify.com/authorize"
    )

    TOKEN_URL = (
        "https://accounts.spotify.com/api/token"
    )

    # ========================================================
    # DEFAULT SCOPES
    # ========================================================

    DEFAULT_SCOPES = [

        "user-read-private",

        "user-read-playback-state",

        "user-modify-playback-state",

        "user-read-currently-playing",

        "user-read-recently-played",
    ]

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self
    ):

        super().__init__()

        # ====================================================
        # CONFIG
        # ====================================================

        self.client_id = str(
            os.getenv(
                "SPOTIFY_CLIENT_ID",
                ""
            )
            or ""
        ).strip()

        self.redirect_uri = str(
            os.getenv(
                "SPOTIFY_REDIRECT_URI",
                "http://127.0.0.1:8888/callback"
            )
            or
            "http://127.0.0.1:8888/callback"
        ).strip()

        # ====================================================
        # HTTP
        # ====================================================

        self.session = (
            requests.Session()
        )

        self.session.headers.update(
            {
                "User-Agent":
                    "LYRx-Music-Player/0.4"
            }
        )

        self.timeout = 15

        # ====================================================
        # TOKEN STATE
        # ====================================================

        self.access_token = ""

        self.refresh_token = ""

        self.expires_at = 0

        self.token_scope = ""

        # ====================================================
        # PKCE STATE
        # ====================================================

        self.code_verifier = ""

        self.oauth_state = ""

        # ====================================================
        # LOAD SAVED TOKEN
        # ====================================================

        self.load_token()

    # ========================================================
    # CONFIGURED
    # ========================================================

    def is_configured(
        self
    ) -> bool:

        return bool(
            self.client_id
            and
            self.redirect_uri
        )

    # ========================================================
    # AVAILABLE
    # ========================================================

    def is_available(
        self
    ) -> bool:

        return bool(
            self.enabled
            and
            self.is_configured()
        )

    # ========================================================
    # AUTHENTICATED
    # ========================================================

    def is_authenticated(
        self
    ) -> bool:

        if not self.access_token:

            return False

        if (
            time.time()
            <
            (
                self.expires_at
                - 60
            )
        ):

            return True

        # ----------------------------------------------------
        # TOKEN EXPIRED
        # ----------------------------------------------------

        if self.refresh_token:

            return self.refresh_access_token()

        return False

    # ========================================================
    # TOKEN DIRECTORY
    # ========================================================

    @staticmethod
    def ensure_token_directory():

        try:

            TOKEN_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

        except Exception as error:

            print(
                "Spotify token directory error:",
                error
            )

    # ========================================================
    # LOAD TOKEN
    # ========================================================

    def load_token(
        self
    ):

        try:

            if not TOKEN_FILE.exists():

                return

            with open(
                TOKEN_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if not isinstance(
                data,
                dict
            ):

                return

            self.access_token = str(
                data.get(
                    "access_token",
                    ""
                )
                or ""
            )

            self.refresh_token = str(
                data.get(
                    "refresh_token",
                    ""
                )
                or ""
            )

            try:

                self.expires_at = float(
                    data.get(
                        "expires_at",
                        0
                    )
                    or 0
                )

            except (
                TypeError,
                ValueError
            ):

                self.expires_at = 0

            self.token_scope = str(
                data.get(
                    "scope",
                    ""
                )
                or ""
            )

        except Exception as error:

            print(
                "Spotify token load error:",
                error
            )

    # ========================================================
    # SAVE TOKEN
    # ========================================================

    def save_token(
        self
    ):

        try:

            self.ensure_token_directory()

            data = {

                "access_token":
                    self.access_token,

                "refresh_token":
                    self.refresh_token,

                "expires_at":
                    self.expires_at,

                "scope":
                    self.token_scope,
            }

            with open(
                TOKEN_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4
                )

        except Exception as error:

            print(
                "Spotify token save error:",
                error
            )

    # ========================================================
    # CLEAR TOKEN
    # ========================================================

    def logout(
        self
    ):

        self.access_token = ""

        self.refresh_token = ""

        self.expires_at = 0

        self.token_scope = ""

        try:

            if TOKEN_FILE.exists():

                TOKEN_FILE.unlink()

        except Exception as error:

            print(
                "Spotify token delete error:",
                error
            )

    # ========================================================
    # PKCE VERIFIER
    # ========================================================

    @staticmethod
    def create_code_verifier() -> str:

        return (
            secrets.token_urlsafe(
                64
            )[:128]
        )

    # ========================================================
    # PKCE CHALLENGE
    # ========================================================

    @staticmethod
    def create_code_challenge(
        verifier: str
    ) -> str:

        digest = hashlib.sha256(
            verifier.encode(
                "utf-8"
            )
        ).digest()

        return (

            base64.urlsafe_b64encode(
                digest
            )

            .decode(
                "utf-8"
            )

            .rstrip(
                "="
            )
        )

    # ========================================================
    # BUILD AUTH URL
    # ========================================================

    def build_authorization_url(
        self
    ) -> str:

        if not self.client_id:

            raise RuntimeError(
                "SPOTIFY_CLIENT_ID is missing."
            )

        self.code_verifier = (
            self.create_code_verifier()
        )

        challenge = (
            self.create_code_challenge(
                self.code_verifier
            )
        )

        self.oauth_state = (
            secrets.token_urlsafe(
                24
            )
        )

        params = {

            "client_id":
                self.client_id,

            "response_type":
                "code",

            "redirect_uri":
                self.redirect_uri,

            "scope":
                " ".join(
                    self.DEFAULT_SCOPES
                ),

            "code_challenge_method":
                "S256",

            "code_challenge":
                challenge,

            "state":
                self.oauth_state,

            "show_dialog":
                "true",
        }

        return (
            self.AUTH_URL
            +
            "?"
            +
            urlencode(
                params
            )
        )

    # ========================================================
    # REDIRECT SERVER INFO
    # ========================================================

    def _callback_server_address(
        self
    ):

        parsed = urlparse(
            self.redirect_uri
        )

        host = (
            parsed.hostname
            or
            "127.0.0.1"
        )

        port = (
            parsed.port
            or
            8888
        )

        return (
            host,
            port
        )

    # ========================================================
    # LOGIN INTERACTIVE
    # ========================================================

    def login_interactive(
        self,
        timeout_seconds=180
    ) -> bool:

        """
        Opens Spotify authorization in the default browser and
        waits for the local callback.

        IMPORTANT:
        Call this from a worker thread later when connected to
        the Qt UI so the UI does not freeze.
        """

        if not self.is_configured():

            self.set_error(
                "Spotify provider is not configured."
            )

            return False

        # ====================================================
        # RESET CALLBACK STATE
        # ====================================================

        SpotifyCallbackHandler.auth_code = ""

        SpotifyCallbackHandler.auth_state = ""

        SpotifyCallbackHandler.auth_error = ""

        # ====================================================
        # BUILD URL
        # ====================================================

        try:

            auth_url = (
                self.build_authorization_url()
            )

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify authorization URL error:",
                error
            )

            return False

        # ====================================================
        # CALLBACK SERVER
        # ====================================================

        host, port = (
            self._callback_server_address()
        )

        try:

            server = HTTPServer(
                (
                    host,
                    port
                ),
                SpotifyCallbackHandler
            )

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify callback server error:",
                error
            )

            return False

        server.timeout = 1

        # ====================================================
        # OPEN BROWSER
        # ====================================================

        print()
        print("=" * 60)

        print(
            "LYRx Spotify Login"
        )

        print("=" * 60)

        print(
            "Opening Spotify authorization..."
        )

        print(
            "Redirect:",
            self.redirect_uri
        )

        print("=" * 60)
        print()

        webbrowser.open(
            auth_url
        )

        # ====================================================
        # WAIT CALLBACK
        # ====================================================

        started = (
            time.time()
        )

        try:

            while (
                time.time()
                -
                started
                <
                timeout_seconds
            ):

                server.handle_request()

                if (
                    SpotifyCallbackHandler.auth_code
                    or
                    SpotifyCallbackHandler.auth_error
                ):

                    break

        finally:

            server.server_close()

        # ====================================================
        # AUTH ERROR
        # ====================================================

        if SpotifyCallbackHandler.auth_error:

            self.set_error(
                SpotifyCallbackHandler.auth_error
            )

            return False

        # ====================================================
        # NO CODE
        # ====================================================

        code = str(
            SpotifyCallbackHandler.auth_code
            or ""
        ).strip()

        if not code:

            self.set_error(
                "Spotify login timed out."
            )

            return False

        # ====================================================
        # VERIFY STATE
        # ====================================================

        callback_state = str(
            SpotifyCallbackHandler.auth_state
            or ""
        )

        if (
            callback_state
            !=
            self.oauth_state
        ):

            self.set_error(
                "Spotify OAuth state mismatch."
            )

            return False

        # ====================================================
        # EXCHANGE CODE
        # ====================================================

        return self.exchange_code(
            code
        )

    # ========================================================
    # EXCHANGE AUTH CODE
    # ========================================================

    def exchange_code(
        self,
        code: str
    ) -> bool:

        code = str(
            code
            or ""
        ).strip()

        if not code:

            return False

        if not self.code_verifier:

            self.set_error(
                "Spotify PKCE verifier is missing."
            )

            return False

        try:

            response = requests.post(

                self.TOKEN_URL,

                data={

                    "client_id":
                        self.client_id,

                    "grant_type":
                        "authorization_code",

                    "code":
                        code,

                    "redirect_uri":
                        self.redirect_uri,

                    "code_verifier":
                        self.code_verifier,
                },

                headers={
                    "Content-Type":
                        "application/x-www-form-urlencoded"
                },

                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            self._apply_token_response(
                data
            )

            self.clear_error()

            print(
                "Spotify authentication successful."
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify token exchange error:",
                error
            )

            return False

    # ========================================================
    # APPLY TOKEN RESPONSE
    # ========================================================

    def _apply_token_response(
        self,
        data
    ):

        if not isinstance(
            data,
            dict
        ):

            raise RuntimeError(
                "Invalid Spotify token response."
            )

        access_token = str(
            data.get(
                "access_token",
                ""
            )
            or ""
        )

        if not access_token:

            raise RuntimeError(
                "Spotify access token missing."
            )

        self.access_token = (
            access_token
        )

        new_refresh_token = str(
            data.get(
                "refresh_token",
                ""
            )
            or ""
        )

        if new_refresh_token:

            self.refresh_token = (
                new_refresh_token
            )

        try:

            expires_in = int(
                data.get(
                    "expires_in",
                    3600
                )
                or 3600
            )

        except (
            TypeError,
            ValueError
        ):

            expires_in = 3600

        self.expires_at = (
            time.time()
            +
            expires_in
        )

        self.token_scope = str(
            data.get(
                "scope",
                self.token_scope
            )
            or
            self.token_scope
        )

        self.save_token()

    # ========================================================
    # REFRESH TOKEN
    # ========================================================

    def refresh_access_token(
        self
    ) -> bool:

        if not self.refresh_token:

            return False

        if not self.client_id:

            return False

        try:

            response = requests.post(

                self.TOKEN_URL,

                data={

                    "grant_type":
                        "refresh_token",

                    "refresh_token":
                        self.refresh_token,

                    "client_id":
                        self.client_id,
                },

                headers={
                    "Content-Type":
                        "application/x-www-form-urlencoded"
                },

                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            self._apply_token_response(
                data
            )

            self.clear_error()

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify token refresh error:",
                error
            )

            return False

    # ========================================================
    # AUTH HEADER
    # ========================================================

    def _headers(
        self
    ) -> Dict[str, str]:

        if not self.is_authenticated():

            raise RuntimeError(
                "Spotify account is not authenticated."
            )

        return {

            "Authorization":
                f"Bearer {self.access_token}",

            "Content-Type":
                "application/json",
        }

    # ========================================================
    # API REQUEST
    # ========================================================

    def _request(
        self,
        method: str,
        endpoint: str,
        params=None,
        json_data=None,
        expected_statuses=None,
    ):

        if expected_statuses is None:

            expected_statuses = {
                200,
                201,
                202,
                204,
            }

        endpoint = str(
            endpoint
            or ""
        )

        if not endpoint.startswith(
            "/"
        ):

            endpoint = (
                "/"
                +
                endpoint
            )

        url = (
            self.API_BASE_URL
            +
            endpoint
        )

        response = self.session.request(

            method=method,

            url=url,

            headers=self._headers(),

            params=params,

            json=json_data,

            timeout=self.timeout,
        )

        # ====================================================
        # TOKEN EXPIRED
        # ====================================================

        if (
            response.status_code
            ==
            401
            and
            self.refresh_token
        ):

            if self.refresh_access_token():

                response = (
                    self.session.request(

                        method=method,

                        url=url,

                        headers=self._headers(),

                        params=params,

                        json=json_data,

                        timeout=self.timeout,
                    )
                )

        # ====================================================
        # ERROR
        # ====================================================

        if (
            response.status_code
            not in expected_statuses
        ):

            message = (
                response.text
                or
                (
                    "Spotify API error "
                    f"{response.status_code}"
                )
            )

            raise RuntimeError(
                message
            )

        # ====================================================
        # NO CONTENT
        # ====================================================

        if response.status_code == 204:

            return {}

        if not response.content:

            return {}

        try:

            return response.json()

        except Exception:

            return {}

    # ========================================================
    # ARTWORK
    # ========================================================

    @staticmethod
    def _best_image(
        album
    ) -> str:

        if not isinstance(
            album,
            dict
        ):

            return ""

        images = album.get(
            "images",
            []
        )

        if not isinstance(
            images,
            list
        ):

            return ""

        if not images:

            return ""

        # Spotify normally returns largest first.
        first = images[0]

        if not isinstance(
            first,
            dict
        ):

            return ""

        return str(
            first.get(
                "url",
                ""
            )
            or ""
        )

    # ========================================================
    # SPOTIFY TRACK -> SONG
    # ========================================================

    def _song_from_track(
        self,
        track
    ) -> Optional[Song]:

        if not isinstance(
            track,
            dict
        ):

            return None

        track_id = str(
            track.get(
                "id",
                ""
            )
            or ""
        )

        title = str(
            track.get(
                "name",
                ""
            )
            or ""
        ).strip()

        if not title:

            return None

        # ====================================================
        # ARTISTS
        # ====================================================

        artists = []

        for artist in (
            track.get(
                "artists",
                []
            )
            or []
        ):

            if not isinstance(
                artist,
                dict
            ):

                continue

            name = str(
                artist.get(
                    "name",
                    ""
                )
                or ""
            ).strip()

            if name:

                artists.append(
                    name
                )

        artist_text = (
            ", ".join(
                artists
            )
        )

        # ====================================================
        # ALBUM
        # ====================================================

        album_data = track.get(
            "album",
            {}
        )

        if not isinstance(
            album_data,
            dict
        ):

            album_data = {}

        album_name = str(
            album_data.get(
                "name",
                ""
            )
            or ""
        )

        image_url = (
            self._best_image(
                album_data
            )
        )

        release_date = str(
            album_data.get(
                "release_date",
                ""
            )
            or ""
        )

        # ====================================================
        # DURATION
        # ====================================================

        try:

            duration_ms = int(
                track.get(
                    "duration_ms",
                    0
                )
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            duration_ms = 0

        duration_seconds = (
            duration_ms
            //
            1000
        )

        # ====================================================
        # URLS
        # ====================================================

        external_urls = track.get(
            "external_urls",
            {}
        )

        if not isinstance(
            external_urls,
            dict
        ):

            external_urls = {}

        spotify_url = str(
            external_urls.get(
                "spotify",
                ""
            )
            or ""
        )

        spotify_uri = str(
            track.get(
                "uri",
                ""
            )
            or ""
        )

        # ====================================================
        # SONG
        # ====================================================
        #
        # No direct audio_url is exposed.
        #
        # Playback will use spotify_uri through
        # SpotifyProvider.play_track().
        # ====================================================

        return Song(

            id=track_id,

            title=title,

            artist=artist_text,

            album=album_name,

            image_url=image_url,

            audio_url="",

            preview_url="",

            duration=duration_seconds,

            provider=self.provider_name,

            downloadable=False,

            download_url="",

            share_url=spotify_url,

            external_url=spotify_url,

            genre="",

            language="",

            release_date=release_date,

            explicit=bool(
                track.get(
                    "explicit",
                    False
                )
            ),

            # ------------------------------------------------
            # Spotify supports full playback through remote
            # playback control, not direct QMediaPlayer.
            # ------------------------------------------------

            full_playback=True,

            preview_available=False,

            metadata={

                "spotify_uri":
                    spotify_uri,

                "spotify_url":
                    spotify_url,

                "spotify_id":
                    track_id,

                "is_playable":
                    bool(
                        track.get(
                            "is_playable",
                            True
                        )
                    ),

                "popularity":
                    int(
                        track.get(
                            "popularity",
                            0
                        )
                        or 0
                    ),

                "playback_mode":
                    "spotify_remote",
            },
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 10,
        market: str = "IN",
    ) -> MusicSearchResult:

        query = str(
            query
            or ""
        ).strip()

        if not query:

            return MusicSearchResult(

                query="",

                songs=[],

                total=0,

                provider=self.provider_name,

                error="Empty Spotify search query.",
            )

        # Spotify's current search endpoint limit is kept small.
        limit = max(
            1,
            min(
                int(limit),
                10
            )
        )

        try:

            data = self._request(

                "GET",

                "/search",

                params={

                    "q":
                        query,

                    "type":
                        "track",

                    "market":
                        market,

                    "limit":
                        limit,
                }
            )

            tracks_container = (
                data.get(
                    "tracks",
                    {}
                )
            )

            if not isinstance(
                tracks_container,
                dict
            ):

                tracks_container = {}

            items = tracks_container.get(
                "items",
                []
            )

            songs = []

            for item in (
                items
                or []
            ):

                song = self._song_from_track(
                    item
                )

                if song is not None:

                    songs.append(
                        song
                    )

            return MusicSearchResult(

                query=query,

                songs=songs,

                total=len(
                    songs
                ),

                provider=self.provider_name,

                error="",
            )

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify search error:",
                error
            )

            return MusicSearchResult(

                query=query,

                songs=[],

                total=0,

                provider=self.provider_name,

                error=str(
                    error
                ),
            )

    # ========================================================
    # SONG SEARCH
    # ========================================================

    def search_song(
        self,
        title: str,
        limit: int = 10,
    ) -> List[Song]:

        result = self.search(
            title,
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # ARTIST SEARCH
    # ========================================================

    def search_artist(
        self,
        artist: str,
        limit: int = 10,
    ) -> List[Song]:

        artist = str(
            artist
            or ""
        ).strip()

        if not artist:

            return []

        result = self.search(

            f'artist:"{artist}"',

            limit=limit,
        )

        songs = list(
            result.songs
            or []
        )

        artist_lower = (
            artist.lower()
        )

        songs.sort(
            key=lambda song: (

                0

                if artist_lower
                in song.display_artist().lower()

                else 1
            )
        )

        return songs

    # ========================================================
    # GENRE
    # ========================================================

    def get_by_genre(
        self,
        genre: str,
        limit: int = 10,
    ) -> List[Song]:

        genre = str(
            genre
            or ""
        ).strip()

        if not genre:

            return []

        result = self.search(

            f'genre:"{genre}"',

            limit=limit,
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # MOOD
    # ========================================================

    def get_by_mood(
        self,
        mood: str,
        limit: int = 10,
    ) -> List[Song]:

        mood = str(
            mood
            or ""
        ).strip()

        if not mood:

            return []

        mood_queries = {

            "happy":
                "happy upbeat",

            "sad":
                "sad emotional",

            "chill":
                "chill relaxing",

            "romantic":
                "romantic love",

            "love":
                "love songs",

            "workout":
                "workout energetic",

            "party":
                "party dance",

            "focus":
                "focus instrumental",

            "sleep":
                "sleep calm",

            "nostalgic":
                "nostalgic classics",
        }

        query = (
            mood_queries.get(
                mood.lower(),
                mood
            )
        )

        result = self.search(
            query,
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # HINDI
    # ========================================================

    def get_hindi(
        self,
        limit: int = 10,
    ) -> List[Song]:

        result = self.search(

            "Bollywood Hindi",

            limit=limit,

            market="IN",
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # ENGLISH
    # ========================================================

    def get_english(
        self,
        limit: int = 10,
    ) -> List[Song]:

        result = self.search(

            "pop hits",

            limit=limit,

            market="US",
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # DEVICES
    # ========================================================

    def get_devices(
        self
    ) -> List[Dict[str, Any]]:

        try:

            data = self._request(

                "GET",

                "/me/player/devices",
            )

            devices = data.get(
                "devices",
                []
            )

            if not isinstance(
                devices,
                list
            ):

                return []

            return devices

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify devices error:",
                error
            )

            return []

    # ========================================================
    # ACTIVE DEVICE
    # ========================================================

    def get_active_device(
        self
    ) -> Optional[Dict[str, Any]]:

        devices = (
            self.get_devices()
        )

        for device in devices:

            if not isinstance(
                device,
                dict
            ):

                continue

            if device.get(
                "is_active"
            ):

                return device

        return None

    # ========================================================
    # CHOOSE DEVICE
    # ========================================================

    def get_best_device_id(
        self
    ) -> str:

        devices = (
            self.get_devices()
        )

        if not devices:

            return ""

        # ====================================================
        # ACTIVE FIRST
        # ====================================================

        for device in devices:

            if (
                isinstance(
                    device,
                    dict
                )
                and
                device.get(
                    "is_active"
                )
            ):

                return str(
                    device.get(
                        "id",
                        ""
                    )
                    or ""
                )

        # ====================================================
        # FIRST AVAILABLE
        # ====================================================

        for device in devices:

            if not isinstance(
                device,
                dict
            ):

                continue

            device_id = str(
                device.get(
                    "id",
                    ""
                )
                or ""
            )

            if device_id:

                return device_id

        return ""

    # ========================================================
    # TRANSFER PLAYBACK
    # ========================================================

    def transfer_playback(
        self,
        device_id: str,
        play: bool = False,
    ) -> bool:

        device_id = str(
            device_id
            or ""
        ).strip()

        if not device_id:

            return False

        try:

            self._request(

                "PUT",

                "/me/player",

                json_data={

                    "device_ids":
                        [
                            device_id
                        ],

                    "play":
                        bool(
                            play
                        ),
                }
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify transfer playback error:",
                error
            )

            return False

    # ========================================================
    # PLAY TRACK
    # ========================================================

    def play_track(
        self,
        song: Song,
        device_id: str = "",
        position_ms: int = 0,
    ) -> bool:

        if song is None:

            return False

        metadata = getattr(
            song,
            "metadata",
            {}
        )

        if not isinstance(
            metadata,
            dict
        ):

            metadata = {}

        spotify_uri = str(

            metadata.get(
                "spotify_uri",
                ""
            )

            or

            ""

        ).strip()

        if not spotify_uri:

            # ------------------------------------------------
            # Build URI from Spotify ID if necessary.
            # ------------------------------------------------

            song_id = str(
                getattr(
                    song,
                    "id",
                    ""
                )
                or ""
            ).strip()

            if song_id:

                spotify_uri = (
                    f"spotify:track:{song_id}"
                )

        if not spotify_uri:

            print(
                "Spotify track URI missing:",
                getattr(
                    song,
                    "title",
                    "Unknown"
                )
            )

            return False

        # ====================================================
        # DEVICE
        # ====================================================

        if not device_id:

            device_id = (
                self.get_best_device_id()
            )

        params = {}

        if device_id:

            params[
                "device_id"
            ] = device_id

        # ====================================================
        # PAYLOAD
        # ====================================================

        payload = {

            "uris":
                [
                    spotify_uri
                ],

            "position_ms":
                max(
                    0,
                    int(
                        position_ms
                    )
                ),
        }

        try:

            self._request(

                "PUT",

                "/me/player/play",

                params=params,

                json_data=payload,
            )

            print(
                "Spotify playing:",
                song.display_title(),
                "-",
                song.display_artist()
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print()
            print("=" * 60)

            print(
                "LYRx SPOTIFY PLAY ERROR"
            )

            print(
                "Song:",
                song.display_title()
            )

            print(
                "Error:",
                error
            )

            print("=" * 60)
            print()

            return False

    # ========================================================
    # RESUME
    # ========================================================

    def resume(
        self,
        device_id: str = "",
    ) -> bool:

        params = {}

        if device_id:

            params[
                "device_id"
            ] = device_id

        try:

            self._request(

                "PUT",

                "/me/player/play",

                params=params,

                json_data={},
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify resume error:",
                error
            )

            return False

    # ========================================================
    # PAUSE
    # ========================================================

    def pause(
        self,
        device_id: str = "",
    ) -> bool:

        params = {}

        if device_id:

            params[
                "device_id"
            ] = device_id

        try:

            self._request(

                "PUT",

                "/me/player/pause",

                params=params,
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify pause error:",
                error
            )

            return False

    # ========================================================
    # NEXT
    # ========================================================

    def next_track(
        self,
        device_id: str = "",
    ) -> bool:

        params = {}

        if device_id:

            params[
                "device_id"
            ] = device_id

        try:

            self._request(

                "POST",

                "/me/player/next",

                params=params,
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify next error:",
                error
            )

            return False

    # ========================================================
    # PREVIOUS
    # ========================================================

    def previous_track(
        self,
        device_id: str = "",
    ) -> bool:

        params = {}

        if device_id:

            params[
                "device_id"
            ] = device_id

        try:

            self._request(

                "POST",

                "/me/player/previous",

                params=params,
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify previous error:",
                error
            )

            return False

    # ========================================================
    # SEEK
    # ========================================================

    def seek(
        self,
        position_ms: int,
        device_id: str = "",
    ) -> bool:

        position_ms = max(
            0,
            int(
                position_ms
            )
        )

        params = {

            "position_ms":
                position_ms
        }

        if device_id:

            params[
                "device_id"
            ] = device_id

        try:

            self._request(

                "PUT",

                "/me/player/seek",

                params=params,
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify seek error:",
                error
            )

            return False

    # ========================================================
    # VOLUME
    # ========================================================

    def set_volume(
        self,
        volume_percent: int,
        device_id: str = "",
    ) -> bool:

        volume_percent = max(
            0,
            min(
                int(
                    volume_percent
                ),
                100
            )
        )

        params = {

            "volume_percent":
                volume_percent
        }

        if device_id:

            params[
                "device_id"
            ] = device_id

        try:

            self._request(

                "PUT",

                "/me/player/volume",

                params=params,
            )

            return True

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify volume error:",
                error
            )

            return False

    # ========================================================
    # CURRENT PLAYBACK
    # ========================================================

    def current_playback(
        self
    ) -> Dict[str, Any]:

        try:

            data = self._request(

                "GET",

                "/me/player",
            )

            if isinstance(
                data,
                dict
            ):

                return data

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify playback state error:",
                error
            )

        return {}

    # ========================================================
    # CURRENT SONG
    # ========================================================

    def current_song(
        self
    ) -> Optional[Song]:

        playback = (
            self.current_playback()
        )

        item = playback.get(
            "item"
        )

        if not isinstance(
            item,
            dict
        ):

            return None

        return self._song_from_track(
            item
        )

    # ========================================================
    # RECENTLY PLAYED
    # ========================================================

    def recently_played(
        self,
        limit: int = 10,
    ) -> List[Song]:

        limit = max(
            1,
            min(
                int(
                    limit
                ),
                50
            )
        )

        try:

            data = self._request(

                "GET",

                "/me/player/recently-played",

                params={
                    "limit":
                        limit
                }
            )

            items = data.get(
                "items",
                []
            )

            if not isinstance(
                items,
                list
            ):

                return []

            songs = []

            seen = set()

            for item in items:

                if not isinstance(
                    item,
                    dict
                ):

                    continue

                track = item.get(
                    "track"
                )

                song = (
                    self._song_from_track(
                        track
                    )
                )

                if song is None:

                    continue

                key = song.unique_key()

                if key in seen:

                    continue

                seen.add(
                    key
                )

                songs.append(
                    song
                )

            return songs

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify recently played error:",
                error
            )

            return []

    # ========================================================
    # PROFILE
    # ========================================================

    def get_profile(
        self
    ) -> Dict[str, Any]:

        try:

            data = self._request(

                "GET",

                "/me",
            )

            if isinstance(
                data,
                dict
            ):

                return data

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "Spotify profile error:",
                error
            )

        return {}

    # ========================================================
    # DEBUG STATUS
    # ========================================================

    def print_status(
        self
    ):

        print()
        print("=" * 60)

        print(
            "LYRx SPOTIFY PROVIDER"
        )

        print("=" * 60)

        print(
            "Configured:",
            self.is_configured()
        )

        print(
            "Authenticated:",
            self.is_authenticated()
        )

        print(
            "Client ID:",
            (
                self.client_id[:6]
                + "..."
                if self.client_id
                else "MISSING"
            )
        )

        print(
            "Redirect URI:",
            self.redirect_uri
        )

        print(
            "Token file:",
            TOKEN_FILE
        )

        print(
            "Last error:",
            (
                self.last_error
                or "None"
            )
        )

        print("=" * 60)
        print()


# ============================================================
# SHARED INSTANCE
# ============================================================

spotify_provider = (
    SpotifyProvider()
)