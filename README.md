# Table de 2 — Vidéo animée style jeu vidéo vintage

Animation 1080x1920 (vertical, 30 fps, ~48 s) : un vaisseau 8-bit tire des lasers
sur les opérations de la table de 2 (2*1 a 2*10). Chaque operation explose et
affiche le bon resultat. Finale : BRAVO!, coupe doree et feux d'artifice.
Le bandeau **MATHS MONDE** est affiche en permanence.

Générée à partir des sources Python de ce dépôt :
- `font5x7.py` — police pixel 5x7
- `timeline.py` — chronologie partagée (video + audio)
- `audio.py` — musique 8-bit + effets sons (numpy -> WAV)
- `render.py` — rendu des frames + encodage ffmpeg (1080x1920)

Regeneration : `python3 audio.py && python3 render.py` (dependances : pillow, numpy, imageio-ffmpeg)
