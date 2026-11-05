"""Explainable content-based ranking for a small synthetic song catalog."""
import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path

MODES = {
    'genre-first': {'genre': 2.0, 'mood': 1.0, 'energy': 1.0},
    'mood-first': {'genre': 1.0, 'mood': 2.0, 'energy': 1.0},
    'energy-first': {'genre': 1.0, 'mood': 1.0, 'energy': 2.0},
}
UNIT_FEATURES = ('energy', 'valence', 'danceability', 'acousticness')


@dataclass
class Song:
    """A synthetic track with descriptive, manually assigned features."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Explicit preferences rather than inferred listening behavior."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def unit_number(value, field):
    """Require a finite number between zero and one, including endpoints."""
    if isinstance(value, bool):
        raise ValueError(f'{field} must be a number between 0 and 1')
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{field} must be a number between 0 and 1') from exc
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError(f'{field} must be a number between 0 and 1')
    return number


def normalize_preferences(user_prefs):
    """Accept dictionary keys and the starter dataclass's field names."""
    if isinstance(user_prefs, UserProfile):
        user_prefs = asdict(user_prefs)
    if not isinstance(user_prefs, dict):
        raise ValueError('Preferences must be a dictionary or UserProfile')
    prefs = {
        'genre': user_prefs.get('genre', user_prefs.get('favorite_genre', '')),
        'mood': user_prefs.get('mood', user_prefs.get('favorite_mood', '')),
        'energy': unit_number(user_prefs.get('energy', user_prefs.get('target_energy', 0.5)), 'target energy'),
    }
    for field in ('genre', 'mood'):
        if not isinstance(prefs[field], str):
            raise ValueError(f'{field} must be text')
        prefs[field] = prefs[field].strip().casefold()
    if 'likes_acoustic' in user_prefs:
        if not isinstance(user_prefs['likes_acoustic'], bool):
            raise ValueError('likes_acoustic must be true or false')
        prefs['likes_acoustic'] = user_prefs['likes_acoustic']
    return prefs


def load_songs(csv_path):
    """Load valid CSV records with explicitly converted numeric fields."""
    songs, ids = [], set()
    with Path(csv_path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        if not set(Song.__dataclass_fields__).issubset(reader.fieldnames or []):
            raise ValueError('Catalog is missing required song columns')
        for row in reader:
            song = dict(row)
            try:
                song['id'] = int(song['id'])
                if song['id'] in ids:
                    raise ValueError('duplicate song ID')
                for field in ('title', 'artist', 'genre', 'mood'):
                    song[field] = song[field].strip()
                    if not song[field]:
                        raise ValueError(f'{field} cannot be empty')
                for field in UNIT_FEATURES:
                    song[field] = unit_number(song[field], field)
                song['tempo_bpm'] = float(song['tempo_bpm'])
                if not math.isfinite(song['tempo_bpm']) or song['tempo_bpm'] <= 0:
                    raise ValueError('tempo_bpm must be positive and finite')
            except (ValueError, TypeError, AttributeError) as exc:
                raise ValueError(f'Invalid catalog row {reader.line_num}: {exc}') from exc
            ids.add(song['id'])
            songs.append(song)
    return songs


def score_song(user_prefs, song, mode='genre-first'):
    """Return a weighted score and the exact contributions explaining it."""
    if mode not in MODES:
        raise ValueError(f'Unknown ranking mode: {mode}')
    prefs = normalize_preferences(user_prefs)
    if isinstance(song, Song):
        song = asdict(song)
    weights, score, reasons = MODES[mode], 0.0, []
    for field in ('genre', 'mood'):
        if prefs[field] and prefs[field] == song[field].strip().casefold():
            points = weights[field]
            score += points
            reasons.append(f'{field} match (+{points:.2f})')
    gap = abs(unit_number(song['energy'], 'song energy') - prefs['energy'])
    points = weights['energy'] * (1.0 - gap)
    score += points
    reasons.append(f'energy gap {gap:.2f} (+{points:.2f})')
    if 'likes_acoustic' in prefs:
        acoustic = unit_number(song['acousticness'], 'acousticness')
        points = 0.25 * (acoustic if prefs['likes_acoustic'] else 1.0 - acoustic)
        score += points
        reasons.append(f'acoustic preference (+{points:.2f})')
    return score, reasons


def recommend_songs(user_prefs, songs, k=5, mode='genre-first', diversity_penalty=0.0):
    """Rank a fresh list, optionally penalizing already-selected artists."""
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError('k must be a positive integer')
    normalize_preferences(user_prefs)
    if mode not in MODES:
        raise ValueError(f'Unknown ranking mode: {mode}')
    if (isinstance(diversity_penalty, bool) or not isinstance(diversity_penalty, (int, float))
            or not math.isfinite(diversity_penalty) or diversity_penalty < 0):
        raise ValueError('diversity_penalty must be finite and non-negative')
    remaining = [(song, *score_song(user_prefs, song, mode)) for song in songs]
    results, artists = [], {}
    while remaining and len(results) < k:
        def adjusted(item):
            return item[1] - diversity_penalty * artists.get(item[0]['artist'].casefold(), 0)
        remaining.sort(key=lambda item: (-adjusted(item), item[0]['id']))
        song, score, reasons = remaining.pop(0)
        artist = song['artist'].casefold()
        penalty = diversity_penalty * artists.get(artist, 0)
        if penalty:
            reasons = reasons + [f'repeated artist (-{penalty:.2f})']
        results.append((song, score - penalty, '; '.join(reasons)))
        artists[artist] = artists.get(artist, 0) + 1
    return results


class Recommender:
    """Preserve the starter OOP interface using the shared scoring rules."""
    def __init__(self, songs):
        self.songs = list(songs)

    def recommend(self, user, k=5):
        """Return the original Song objects in weighted-score order."""
        by_id = {song.id: song for song in self.songs}
        ranked = recommend_songs(user, [asdict(song) for song in self.songs], k)
        return [by_id[song['id']] for song, _, _ in ranked]

    def explain_recommendation(self, user, song):
        """Explain the actual score instead of producing a generic claim."""
        return '; '.join(score_song(user, song)[1])
