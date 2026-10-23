"""
core/theme_manager.py — Dynamic Subject-Based Theming System for GARILA.
Contains the 50 predefined topic themes with Kurdish/English names, Hex codes,
keyword detection, and smooth color interpolation.
"""

from __future__ import annotations

import re
import colorsys
from typing import NamedTuple

class ThemePreset(NamedTuple):
    index: int
    key: str
    name_ku: str
    name_en: str
    hex_code: str
    keywords: list[str]

# 💡 50 Subject & Theme Specifications
THEME_PRESETS: dict[str, ThemePreset] = {
    "tech": ThemePreset(
        1, "tech", "تەکنەلۆژیا و بەرمەجە", "General Tech/Dev", "#00F0FF",
        ["tech", "technology", "programming", "code", "python", "developer", "software", "hardware", "بەرمەجە", "تەکنەلۆژیا", "کۆد", "بەرنامەسازی", "پایتۆن", "کۆمپیوتەر"]
    ),
    "cybersecurity": ThemePreset(
        2, "cybersecurity", "ئاسایشی سایبەری و هاکینگ", "Cybersecurity/OSINT", "#00FF66",
        ["security", "cyber", "hack", "hacking", "osint", "firewall", "malware", "virus", "ئاسایش", "سایبەر", "هاک", "هاکینگ", "ڤایرۆس", "پاراستن"]
    ),
    "ai": ThemePreset(
        3, "ai", "زیرەکیی دەستکرد و ڕۆبۆتێک", "AI & Robotics", "#8A2BE2",
        ["ai", "robot", "robotics", "artificial intelligence", "machine learning", "neural", "deep learning", "ڕۆبۆت", "زیرەکی دەستکرد", "مۆدێل", "ئەی ئای"]
    ),
    "casual": ThemePreset(
        4, "casual", "گفتوگۆی ئاسایی و ڕودانی ڕۆژانە", "Casual Conversation", "#98FF98",
        ["hello", "hi", "how are you", "choni", "slaw", "bashi", "سڵاو", "چۆنی", "باشی", "قسە", "گفتوگۆ", "ڕۆژباش", "سوپاس"]
    ),
    "politics": ThemePreset(
        5, "politics", "سیاسەت و پێوەندییە نێودەوڵەتییەکان", "Politics", "#DC143C",
        ["politics", "government", "president", "minister", "election", "diplomat", "سیاسەت", "حکومەت", "سەرۆک", "هەڵبژاردن", "پەرلەمان", "دەوڵەت"]
    ),
    "history": ThemePreset(
        6, "history", "مێژوو و شوێنەوارناسی", "History & Archaeology", "#CD7F32",
        ["history", "ancient", "archaeology", "empire", "century", "war", "مێژوو", "شوێنەوار", "ئیمپراتۆریەت", "کۆن", "سەدەی", "مێژووی"]
    ),
    "economics": ThemePreset(
        7, "economics", "ئابووری، دراو و بازاڕ", "Economics & Finance", "#50C878",
        ["economy", "finance", "money", "market", "bank", "dollar", "trade", "ئابووری", "دراو", "پارە", "بانک", "دۆلار", "بازاڕ", "سەرمایە"]
    ),
    "crypto": ThemePreset(
        8, "crypto", "کریپتۆ و بلۆکچێن", "Crypto & Web3", "#FFD700",
        ["crypto", "bitcoin", "blockchain", "ethereum", "btc", "eth", "web3", "کریپتۆ", "بیتکۆین", "بلۆکچێن", "ئیسریۆم", "دراوی دیجیتاڵی"]
    ),
    "physics": ThemePreset(
        9, "physics", "فیزیا و زانستی گەردوون", "Physics & Space", "#4B0082",
        ["physics", "space", "universe", "quantum", "gravity", "galaxy", "nasa", "فیزیا", "گەردوون", "بۆشایی", "کوانتەم", "کێشکردن", "ئەستێرە"]
    ),
    "chemistry": ThemePreset(
        10, "chemistry", "کیمیا و ماددەکان", "Chemistry & Materials", "#7FFF00",
        ["chemistry", "chemical", "molecule", "atom", "reaction", "acid", "element", "کیمیا", "ماددە", "گەردیلە", "تێکەڵە", "ترش"]
    ),
    "mathematics": ThemePreset(
        11, "mathematics", "بیرکاری و ئامار", "Mathematics & Logic", "#1E90FF",
        ["math", "mathematics", "algebra", "calculus", "geometry", "statistic", "بیرکاری", "ئامار", "هاوکێشە", "ژمارە", "حساب"]
    ),
    "medical": ThemePreset(
        12, "medical", "پزیشکی و تەندروستی", "Medical & Health", "#008080",
        ["doctor", "medicine", "health", "hospital", "disease", "treatment", "cure", "پزیشک", "تەندروستی", "دەرمان", "نەخۆشخانە", "چارەسەر", "نەخۆشی"]
    ),
    "sports": ThemePreset(
        13, "sports", "وەرزش و فیتنس", "Sports & Fitness", "#FF4500",
        ["sport", "sports", "football", "fitness", "gym", "workout", "match", "وەرزش", "یاری", "تۆپی پێ", "فیتنس", "جیم", "مەشق", "یاریزان"]
    ),
    "art": ThemePreset(
        14, "art", "هونەر و دیزاین", "Art & Design", "#FF00FF",
        ["art", "design", "drawing", "painting", "graphic", "illustration", "هونەر", "دیزاین", "نیگارکێشان", "تابلۆ", "ڕەنگ"]
    ),
    "music": ThemePreset(
        15, "music", "مۆسیقا و دەنگ", "Music & Audio", "#FF69B4",
        ["music", "song", "audio", "singer", "melody", "sound", "guitar", "گۆرانی", "مۆسیقا", "ئاواز", "دەنگ", "ساز", "گۆرانیبێژ"]
    ),
    "photography": ThemePreset(
        16, "photography", "فۆتۆگرافی و ڤیدیۆگرافی", "Photography/Media", "#FFFACD",
        ["photo", "photography", "camera", "video", "videography", "lens", "وێنە", "کامێرا", "فۆتۆگرافەر", "ڤیدیۆ", "لێنز"]
    ),
    "cinema": ThemePreset(
        17, "cinema", "سینەما و فیلم", "Cinema & Movies", "#8B0000",
        ["movie", "film", "cinema", "actor", "hollywood", "director", "series", "فیلم", "سینەما", "ئەکتەر", "دەرهێنەر", "دراما", "زنجیرە"]
    ),
    "gaming": ThemePreset(
        18, "gaming", "کایە ڤیدیۆییەکان", "Gaming & Esports", "#9400D3",
        ["game", "gaming", "esport", "playstation", "xbox", "steam", "gamer", "گەمە", "یاری ڤیدیۆیی", "گیمینگ", "پلەیستەیشن", "ئێکس بۆکس"]
    ),
    "philosophy": ThemePreset(
        19, "philosophy", "فەلسەفە و دەروونناسی", "Philosophy & Psychology", "#708090",
        ["philosophy", "psychology", "mind", "soul", "thought", "logic", "فەلسەفە", "دەروونناسی", "بیرکردنەوە", "ئاوەز", "مێشک"]
    ),
    "religion": ThemePreset(
        20, "religion", "ئایین و بەها ڕەوشتییەکان", "Religion & Ethics", "#F0E68C",
        ["religion", "islam", "christianity", "quran", "faith", "ethics", "moral", "ئایین", "ئیسلام", "قورئان", "ئیمان", "ڕەوشت", "باوەڕ"]
    ),
    "law": ThemePreset(
        21, "law", "یاسا و دادپەروەری", "Law & Legal", "#000080",
        ["law", "legal", "court", "judge", "justice", "lawyer", "crime", "یاسا", "دادگا", "دادوەر", "دادپەروەری", "پارێزەر", "تاوان"]
    ),
    "linguistics": ThemePreset(
        22, "linguistics", "زمان و زاراوەناسی", "Linguistics & Languages", "#E6E6FA",
        ["language", "linguistics", "grammar", "translation", "english", "kurdish", "زمان", "زاراوە", "ڕێزمان", "وەرگێڕان", "کوردی", "ئینگلیزی"]
    ),
    "literature": ThemePreset(
        23, "literature", "ئەدەب و شێعر", "Literature & Poetry", "#B76E79",
        ["literature", "poetry", "poem", "poet", "novel", "author", "writer", "ئەدەب", "شیعر", "شاعیر", "ڕۆمان", "نووسەر", "پەخشان"]
    ),
    "geography": ThemePreset(
        24, "geography", "جۆگرافیا و نەخشەسازی", "Geography & Maps", "#556B2F",
        ["geography", "map", "country", "city", "mountain", "river", "continent", "جۆگرافیا", "نەخشە", "وڵات", "شار", "چیا", "ڕووبار"]
    ),
    "weather": ThemePreset(
        25, "weather", "کەشوهەوا و ژینگە", "Weather & Environment", "#87CEEB",
        ["weather", "climate", "rain", "temperature", "forecast", "cloud", "storm", "کەشوهەوا", "باران", "پلەی گەرمی", "هەور", "بای", "کەش"]
    ),
    "automotive": ThemePreset(
        26, "automotive", "ئۆتۆمبێل و پیشەسازی", "Automotive & Engines", "#FFCC00",
        ["car", "cars", "automotive", "engine", "vehicle", "bmw", "mercedes", "ئۆتۆمبێل", "سەیارە", "بزوێنەر", "مەکینە", "تایەر"]
    ),
    "aviation": ThemePreset(
        27, "aviation", "فڕین و زانستی فڕۆکەوانی", "Aviation", "#4682B4",
        ["aviation", "airplane", "plane", "flight", "pilot", "airport", "فڕۆکە", "فڕین", "فڕۆکەوان", "فڕۆکەخانە", "گەشت"]
    ),
    "culinary": ThemePreset(
        28, "culinary", "خواردن و لێنانی چێشت", "Culinary & Food", "#FF7F50",
        ["food", "cooking", "recipe", "kitchen", "restaurant", "chef", "خواردن", "چێشت", "چێشتلێنان", "خواردەمەنی", "چێشتخانە", "شەربەت"]
    ),
    "travel": ThemePreset(
        29, "travel", "گەشتوگوزار و گەشتکردن", "Travel & Tourism", "#40E0D0",
        ["travel", "tourism", "hotel", "tourist", "vacation", "trip", "گەشت", "گەشتوگوزار", "هوتێل", "سەفەر", "گەشتیاری"]
    ),
    "zoology": ThemePreset(
        30, "zoology", "ئاژەڵناسی و سروشت", "Zoology & Wildlife", "#228B22",
        ["animal", "animals", "wildlife", "zoology", "bird", "lion", "mammal", "ئاژەڵ", "ئاژەڵان", "باڵندە", "سروشت", "دڕندە"]
    ),
    "botany": ThemePreset(
        31, "botany", "زانستی ڕووەک", "Botany & Flora", "#32CD32",
        ["plant", "plants", "botany", "tree", "flower", "leaf", "flora", "ڕووەک", "دار", "گوڵ", "دارستان", "گەڵا"]
    ),
    "education": ThemePreset(
        32, "education", "فێربوون و پەروەردە", "Education & Academic", "#4169E1",
        ["education", "school", "university", "study", "student", "teacher", "exam", "پەروەردە", "قوتابخانە", "زانکۆ", "خوێندن", "مامۆستا", "تاقیکردنەوە"]
    ),
    "business": ThemePreset(
        33, "business", "بەڕێوەبردن و بازرگانی", "Business & Management", "#4682B4",
        ["business", "management", "company", "startup", "strategy", "marketing", "بازرگانی", "بەڕێوەبردن", "کۆمپانیا", "پڕۆژە", "ستراتیژ"]
    ),
    "marketing": ThemePreset(
        34, "marketing", "بازاڕگەری و ڕیکلام", "Marketing & Ads", "#FFA500",
        ["marketing", "advertising", "campaign", "branding", "sales", "social media", "ڕیکلام", "مارکێتینگ", "فرۆشتن", "براند"]
    ),
    "news": ThemePreset(
        35, "news", "هەواڵ و ڕووداوە فریاگوزارییەکان", "Breaking News", "#FF0000",
        ["news", "breaking", "headline", "report", "crisis", "alert", "هەواڵ", "بەپەلە", "ڕووداو", "ڕاپۆرت", "ئاگاداری"]
    ),
    "astrology": ThemePreset(
        36, "astrology", "کەشوهەوای بۆشایی گەردوون", "Astrology & Cosmos", "#800080",
        ["nebula", "cosmos", "astronomy", "comet", "supernova", "planet", "هەسارە", "کەشتی ئاسمانی", "گەردوونی"]
    ),
    "architecture": ThemePreset(
        37, "architecture", "بیناسازی و ئەندازیاری", "Architecture", "#D3D3D3",
        ["architecture", "building", "construction", "engineering", "structure", "بیناسازی", "ئەندازیاری", "تەلارسازی", "باڵەخانە"]
    ),
    "fashion": ThemePreset(
        38, "fashion", "فاشیۆن و پۆشاک", "Fashion & Style", "#B76E79",
        ["fashion", "style", "clothing", "dress", "outfit", "brand", "model", "پۆشاک", "جلوبەرگ", "فاشیۆن", "مۆدێل", "ستایل"]
    ),
    "chess": ThemePreset(
        39, "chess", "یارییە فیکرییەکان و شەترەنج", "Chess & Puzzles", "#36454F",
        ["chess", "puzzle", "riddle", "strategy game", "board game", "شەترەنج", "مەتەڵ", "یاری فیکری"]
    ),
    "family": ThemePreset(
        40, "family", "خێزان و منداڵان", "Family & Parenting", "#FFDAB9",
        ["family", "parents", "children", "baby", "mother", "father", "kid", "خێزان", "منداڵ", "دایک", "باوک", "پەروەردەی منداڵ"]
    ),
    "mindfulness": ThemePreset(
        41, "mindfulness", "ڕاهێنانی دەروونی و هۆشیاری", "Mindfulness", "#E0FFFF",
        ["meditation", "mindfulness", "peace", "calm", "relax", "yoga", "ئارامی", "هێمنی", "تێڕامان", "مێدیتەیشن", "هۆشیاری"]
    ),
    "humor": ThemePreset(
        42, "humor", "کۆمیدیا و کات بەسەربردن", "Humor & Memes", "#FFFF00",
        ["joke", "humor", "funny", "laugh", "meme", "comedy", "قسەخۆش", "پێکەنین", "کۆمیدیا", "نوکتە", "مەمە"]
    ),
    "mythology": ThemePreset(
        43, "mythology", "ئەفسانە و چیڕۆکی خەیاڵی", "Mythology & Fantasy", "#4B0082",
        ["mythology", "myth", "legend", "fantasy", "dragon", "magic", "ئەفسانە", "داستان", "خەیاڵی", "جادوو"]
    ),
    "maritime": ThemePreset(
        44, "maritime", "پیشەسازی دەریایی و کەشتیوانی", "Maritime", "#00008B",
        ["sea", "ocean", "ship", "boat", "maritime", "sailor", "دەریایی", "کەشتی", "زەریا", "کەشتیوان", "دەریا"]
    ),
    "energy": ThemePreset(
        45, "energy", "وزەی نوێبووەوە و کارەبا", "Renewable Energy", "#00FF00",
        ["energy", "solar", "wind", "electricity", "battery", "power", "renewable", "وزە", "کارەبا", "خۆر", "باتری", "سۆلار"]
    ),
    "agriculture": ThemePreset(
        46, "agriculture", "باخچەوانی و کشتوکاڵ", "Agriculture", "#8B4513",
        ["agriculture", "farming", "crop", "harvest", "soil", "farm", "کشتوکاڵ", "جووتیاری", "بەرهەم", "باخچە", "خاک"]
    ),
    "diplomacy": ThemePreset(
        47, "diplomacy", "دیپلۆماسی و پەیماننامەکان", "Diplomacy", "#6A5ACD",
        ["diplomacy", "treaty", "ambassador", "alliance", "peace", "agreement", "دیپلۆماسی", "پەیماننامە", "باڵیۆز", "ڕێککەوتن"]
    ),
    "forensics": ThemePreset(
        48, "forensics", "زانستی بەڵگەکان و پزیشکی دادوەری", "Forensics", "#8A00C4",
        ["forensics", "evidence", "investigation", "crime scene", "dna", "پزیشکی دادوەری", "بەڵگە", "لێکۆڵینەوە", "تاوانناسی"]
    ),
    "safety": ThemePreset(
        49, "safety", "فریاگوزاری یەکەم و سەلامەتی", "Safety & Emergency", "#FFEE00",
        ["safety", "emergency", "first aid", "fire", "rescue", "hazard", "فریاگوزاری", "سەلامەتی", "مەترسی", "ئاگرکوژێنەوە", "فریاکەوتن"]
    ),
    "idle": ThemePreset(
        50, "idle", "بێدەنگی / باری چاوەڕوانی", "Idle / System Standby", "#2F4F4F",
        ["idle", "standby", "sleep", "wait", "بێدەنگی", "چاوەڕوانی", "خەوتن"]
    ),
}

_THEME_TAG_RE = re.compile(r"\[THEME:([^\]:]+)(?::([^\]]+))?\]", re.IGNORECASE)


def parse_and_strip_theme_tag(text: str) -> tuple[str, str | None]:
    """
    Extracts [THEME:CategoryName:Hex] or [THEME:#HEX] or [THEME:category_name]
    from incoming text, returns (cleaned_text, matched_hex).
    """
    m = _THEME_TAG_RE.search(text)
    if not m:
        return text, None
    tag_content = m.group(1).strip()
    optional_hex = m.group(2).strip() if m.group(2) else None
    
    cleaned = _THEME_TAG_RE.sub("", text).strip()
    
    # If explicit hex was provided
    if optional_hex and optional_hex.startswith("#") and len(optional_hex) in (4, 7):
        return cleaned, optional_hex
    if tag_content.startswith("#") and len(tag_content) in (4, 7):
        return cleaned, tag_content
    
    # Look up by key or category name
    key_low = tag_content.lower()
    for preset in THEME_PRESETS.values():
        if key_low in (preset.key, preset.name_en.lower(), preset.name_ku.lower()):
            return cleaned, preset.hex_code
            
    return cleaned, None


def classify_text_theme(text: str) -> ThemePreset:
    """
    Classifies the text against the 50 predefined subject presets using
    keyword and semantic matching. Defaults to 'tech' (#00F0FF) if no match.
    """
    if not text:
        return THEME_PRESETS["tech"]
        
    low = text.lower()
    best_match = None
    max_score = 0
    
    for preset in THEME_PRESETS.values():
        score = 0
        for kw in preset.keywords:
            if kw in low:
                score += len(kw) * 2
        if score > max_score:
            max_score = score
            best_match = preset
            
    if best_match and max_score > 0:
        return best_match
    return THEME_PRESETS["tech"]


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def interpolate_hex(hex1: str, hex2: str, t: float) -> str:
    """Linearly interpolates between two hex colors, t in [0.0, 1.0]."""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    t = max(0.0, min(1.0, float(t)))
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex(r, g, b)
