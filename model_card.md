# Model Card: VibeFinder 1.0

## 1. Model Name
VibeFinder 1.0, a content-based classroom simulation.

## 2. Intended Use and Goal
Rank a small music catalog for explicit genre, mood, and energy preferences. Use it to understand data, scoring, and ranking. It is not a production recommender, a trained model, or a diagnosis of someone's emotional state. Do not use it to make claims about actual music popularity or personal characteristics.

## 3. How the Model Works / Algorithm Summary
A genre match and a mood match add points. Energy earns more when the song is closer to the requested energy, whether the target is high or low. The chosen strategy changes the relative weights. The optional acoustic preference has a smaller weight. Each song is scored before ranking; the top K tracks are returned with the actual scoring reasons. A separate artist penalty can trade relevance for variety. Both the functional and OOP interfaces use these same rules.

## 4. Data
There are 20 synthetic songs: ten starter rows and ten AI-generated additions. Every row has ID, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, and acousticness. No personal data or external listening histories are used. Counts by genre: {"ambient": 1, "classical": 1, "country": 1, "edm": 1, "folk": 1, "hip-hop": 1, "indie pop": 1, "jazz": 1, "latin": 1, "lofi": 4, "pop": 3, "rnb": 1, "rock": 2, "synthwave": 1}. Artist names, titles, moods and numeric features are fictional illustrative data. Several artists have repeated tracks so variety can be tested.

## 5. Strengths
The rules are deterministic and their contributions are visible. The pop, lofi, and rock profiles select matching genres first. Low-energy users are not penalized merely because they prefer low energy. Inputs such as NaN, infinity, out-of-range numbers, and invalid result counts are rejected. Structured tables show both the score and why it was assigned.

## 6. Limitations and Bias
Twenty fictional tracks do not represent musical taste. Genre matching treats related labels as unrelated and can over-favor an exact label. The ambient/sad/high-energy profile cannot be perfectly satisfied because the catalog lacks that combination. Repeated artists dominate some lists unless the optional diversity penalty is used. A penalty improves artist variety, but does not prove broader fairness. There is no evidence that these hand-assigned attributes predict real enjoyment.

## 7. Evaluation
Actual outputs are in README code blocks and evidence/run-1.txt through run-5.txt. All 24 tests passed. Pop first selects Weekend Skyline, lofi selects Library Rain, and rock selects Storm Runner. Pop versus lofi changes genre, mood and energy; pop versus rock keeps high energy but changes genre and mood; lofi versus rock changes low/chill preferences to high/intense ones. These pairwise differences match the scoring rules.

The weight-shift experiment uses one unchanged conflicting profile: ambient/sad/0.95. Genre-first selects Spacewalk Thoughts; energy-first selects Electric Horizon. This is an instructive result: changing weights changes what 'best' means without changing any song. Artist penalty 2 moves another artist ahead of a second Neon Echo track. This measures rule behavior, not recommendation accuracy against real listener labels.

## 8. Future Work
Collect consented preference feedback and evaluate against held-out choices. Support multiple genre and mood labels. Compare diversity and relevance metrics on a larger, less imbalanced catalog.

## 9. Engineering Reflection and AI Collaboration
This submission was generated and tested with Codex assistance. The main learning point is the separation of data features, user preferences, scoring, and ranking. A simple weighted rule can look personalized while still missing important musical context. AI supplied implementation and tests; the saved arithmetic and test outputs are the evidence used to check correctness.

One accepted design suggestion was to use closeness to target energy, rather than give every high-energy song more points. One alternative not accepted as written was adding a web interface and additional data libraries: this version uses a CLI and Python's csv module so the whole path stays small. This describes the implementation decisions made during AI-assisted work; it does not claim a human completed independent experiments or listened to the fictional tracks. A useful next extension is an integrated reliability layer that refuses unsupported requests and audits the output.
