"""Checks for numeric ranking, catalog loading, modes, and invalid input."""
import copy
import pytest
from src.main import CATALOG, PROFILES
from src.recommender import load_songs, recommend_songs, score_song


def test_catalog_records_are_typed_and_diverse():
    songs = load_songs(CATALOG)
    assert len(songs) == 20
    assert len({s['id'] for s in songs}) == 20
    assert all(isinstance(s['energy'], float) for s in songs)
    assert len({s['genre'] for s in songs}) >= 10


def test_exact_score_and_truthful_explanation():
    score, reasons = score_song(PROFILES['pop'], load_songs(CATALOG)[0])
    assert score == pytest.approx(3.98)
    assert 'genre match (+2.00)' in reasons
    assert 'energy gap 0.02 (+0.98)' in reasons


def test_nearer_energy_scores_higher():
    song = load_songs(CATALOG)[0]
    assert score_song({'energy': 0.82}, song)[0] > score_song({'energy': 0}, song)[0]


@pytest.mark.parametrize('name,genre', [('pop', 'pop'), ('lofi', 'lofi'), ('rock', 'rock')])
def test_profiles_change_top_results(name, genre):
    result = recommend_songs(PROFILES[name], load_songs(CATALOG))
    assert len(result) == 5
    assert result[0][0]['genre'] == genre
    assert all(result[i][1] >= result[i + 1][1] for i in range(4))


def test_does_not_mutate_catalog():
    songs = load_songs(CATALOG)
    before = copy.deepcopy(songs)
    recommend_songs(PROFILES['rock'], songs)
    assert songs == before


def test_modes_change_conflicting_preferences():
    songs = load_songs(CATALOG)
    prefs = {'genre': 'rock', 'mood': 'chill', 'energy': 0.35}
    assert recommend_songs(prefs, songs, mode='genre-first')[0][0]['genre'] == 'rock'
    assert recommend_songs(prefs, songs, mode='mood-first')[0][0]['mood'] == 'chill'


def test_artist_penalty_changes_selection():
    songs = load_songs(CATALOG)
    baseline = recommend_songs(PROFILES['pop'], songs, k=3)
    diverse = recommend_songs(PROFILES['pop'], songs, k=3, diversity_penalty=2)
    assert baseline[1][0]['artist'] == baseline[0][0]['artist']
    assert diverse[1][0]['artist'] != diverse[0][0]['artist']


@pytest.mark.parametrize('energy', [float('nan'), float('inf'), -0.1, 1.1, True, 'bad'])
def test_bad_preferences_rejected(energy):
    with pytest.raises(ValueError):
        recommend_songs({'energy': energy}, load_songs(CATALOG))


@pytest.mark.parametrize('k', [0, -1, True, 1.5])
def test_bad_k_rejected(k):
    with pytest.raises(ValueError):
        recommend_songs(PROFILES['pop'], load_songs(CATALOG), k=k)


def test_missing_columns_rejected(tmp_path):
    path = tmp_path / 'bad.csv'
    path.write_text('id,title\n1,test\n')
    with pytest.raises(ValueError, match='missing required'):
        load_songs(path)


def test_case_and_whitespace_normalized():
    songs = load_songs(CATALOG)
    assert recommend_songs({'genre': ' POP ', 'mood': 'Happy', 'energy': 0.8}, songs) == recommend_songs(PROFILES['pop'], songs)


def test_empty_catalog_does_not_fabricate_songs():
    assert recommend_songs(PROFILES['pop'], []) == []
