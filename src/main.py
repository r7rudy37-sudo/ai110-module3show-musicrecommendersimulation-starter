"""Run reproducible preference experiments from the command line."""
import argparse
from pathlib import Path
from .recommender import MODES, load_songs, recommend_songs

PROFILES = {
    'pop': {'genre': 'pop', 'mood': 'happy', 'energy': 0.8},
    'lofi': {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35},
    'rock': {'genre': 'rock', 'mood': 'intense', 'energy': 0.9},
    'conflicting': {'genre': 'ambient', 'mood': 'sad', 'energy': 0.95},
}
CATALOG = Path(__file__).resolve().parents[1] / 'data' / 'songs.csv'


def format_recommendations(results):
    """Display title, artist, score and reasons for every result."""
    lines = [f"{'#':<3} {'Title':<25} {'Artist':<19} Score", '-' * 58]
    for i, (song, score, reason) in enumerate(results, 1):
        lines.extend([f"{i:<3} {song['title']:<25} {song['artist']:<19} {score:.2f}", f'    Because: {reason}'])
    return '\n'.join(lines)


def main():
    """Select a profile and ranking strategy without changing source code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=['all', *PROFILES], default='all')
    parser.add_argument('--mode', choices=list(MODES), default='genre-first')
    parser.add_argument('--diversity', type=float, default=0.0)
    parser.add_argument('--k', type=int, default=5)
    args = parser.parse_args()
    songs = load_songs(CATALOG)
    print(f'Loaded songs: {len(songs)} | mode: {args.mode}')
    names = ['pop', 'lofi', 'rock'] if args.profile == 'all' else [args.profile]
    try:
        for name in names:
            print(f'\nProfile: {name} {PROFILES[name]}')
            print(format_recommendations(recommend_songs(PROFILES[name], songs, args.k, args.mode, args.diversity)))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
