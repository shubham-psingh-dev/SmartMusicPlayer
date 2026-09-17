from dataclasses import dataclass
from typing import Dict, Tuple

from ui.kids.kids_parental import KidsParentalControls

@dataclass(frozen=True)
class KidsSection:
    route: str
    title: str
    emoji: str
    description: str
    queries: Tuple[str, ...]
    hints: Tuple[str, ...]

KIDS_SECTIONS: Dict[str, KidsSection] = {
    "Kids Music": KidsSection("Kids Music","Kids Music","🎧",
        "Songs, sing-alongs and gentle listening for children.",
        ("nursery rhymes kids","children songs nursery","kids sing along"),
        ("kids","children","nursery","rhyme","lullaby","baby","twinkle",
         "wheels on the bus","old macdonald","baa baa","five little",
         "cocomelon","super simple","pinkfong")),
    "Stories": KidsSection("Stories","Audible Stories","📖",
        "Story-like audio and spoken-word discovery.",
        ("children bedtime story","kids moral story","fairy tale children"),
        ("story","stories","fairy","tale","bedtime","children","kids",
         "cinderella","moral")),
    "Poems & Rhymes": KidsSection("Poems & Rhymes","Poems & Rhymes","✨",
        "Rhymes, poems and playful little verses.",
        ("nursery rhyme children","kids rhymes","children poem"),
        ("rhyme","rhymes","nursery","poem","poems","kids","children",
         "twinkle","baa baa","humpty")),
    "Spiritual": KidsSection("Spiritual","Spiritual","🪷",
        "Calm devotional listening selected with child-oriented hints.",
        ("kids devotional songs","children prayer song","kids spiritual music"),
        ("kids","children","child","prayer","devotional","bhajan","mantra",
         "spiritual","bal","baby")),
}
BLOCKED = ("explicit","18+","nsfw","adult only","sexual")

def _text(song):
    return " ".join(str(getattr(song,k,"") or "") for k in
                    ("title","artist","album")).lower()

def matches_kids_section(song, route):
    text = _text(song)
    section = KIDS_SECTIONS.get(route)
    controls = KidsParentalControls()
    return bool(
        section
        and not any(x in text for x in BLOCKED)
        and controls.song_allowed(song)
        and any(x in text for x in section.hints)
    )

def playable_url(song):
    if song is None: return ""
    try:
        fn = getattr(song,"playable_url",None)
        if callable(fn):
            value = str(fn() or "").strip()
            if value: return value
    except Exception: pass
    return str(getattr(song,"audio_url","") or
               getattr(song,"preview_url","") or "").strip()
