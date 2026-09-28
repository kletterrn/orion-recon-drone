S-8000 BANDEROL-INSPIRED SYNTHETIC GAME AUDIO
==========================================
Created: 2026-09-27

AUTHENTICITY
These are original procedural sound-design sketches, NOT recordings of an
S-8000 Banderol. They are not a verified acoustic match to the real system.
The pitch, turbine start timing, motion and impact textures are artistic
choices. The impacts are generic effects, not a reconstruction of a real
warhead or a model of explosive yield, blast pressure or blast distance.
No third-party audio recordings or combat footage are embedded.

REFERENCE FOR PROPULSION TYPE ONLY
Ukraine's Defence Intelligence, War & Sanctions component catalogue:
"S8000 Banderol cruise missile / Turbojet engine SW800Pro-A95"
https://war-sanctions.gur.gov.ua/en/components/6040
Viewed 2026-09-27. This is the catalogue's identification and is not an
acoustic measurement. It informed the broad turbojet-like design direction
rather than an Orion-style piston/propeller sound. The search did not yield
a clean Banderol flying/impact recording that could be authenticated.

LISTEN
Banderol_STYLE_SYNTHETIC_preview.mp3 (51 seconds)
A WAV master of the same preview is also included.
Start at low playback volume: the preview contains sudden impact sounds.

00:00-00:07  Illustrative turbine spool-up
00:07-00:13  Steady engine flight sound
00:14-00:25  Close left-to-right stereo flyby
00:26-00:39  Incoming flight followed by a generic impact at 00:32
00:40-00:50  Distant generic impact with rolling tail
There are short silent gaps and a silent ending between/after examples.
These are edited examples, not one physically consistent flight sequence.

SOURCE ASSETS
All nine WAV source assets: 48,000 Hz, 16-bit PCM.
01  turbine_spoolup: mono, 7 seconds; illustrative, not launch instructions.
02  flight_engine_LOOP: mono, 12 seconds; dry continuous source texture.
03  flight_engine_high_LOOP: mono, 12 seconds; brighter alternative texture.
04  flyby_close: stereo, 11 seconds; baked motion and pitch change.
05  flyby_distant: stereo, 12 seconds; baked motion and distance-like EQ.
06  incoming_and_impact: stereo, 13 seconds; edited illustrative sequence.
07  impact_close: mono, 7 seconds; generic sharp impact and decay.
08  impact_distant: mono, 10 seconds; generic filtered boom and tail.
09  debris_tail: mono, 5 seconds; separate subtle rubble layer.

LOOP / IMPLEMENTATION NOTES
02 and 03 are periodic textures intended to loop over their full 576,000
frames. The sample-to-sample change at each wrap was checked against the
normal adjacent-sample variation. Playback behavior still needs testing in
your chosen audio engine. Apply start/stop fades in the playback system.
The two loops are alternative textures, not calibrated engine-power modes.

The mono engine assets do not contain baked stereo movement or Doppler.
The rendered flybys and the combined incoming/impact example do. They are
separate preview/cinematic assets, not substitutes for dry source emitters.
The impact distance labels describe a designed listening impression; no
physical distance, explosive mass or real-world sound pressure is implied.

These are source audio files, not a tested Arma Reforger sound configuration.
No Enfusion integration, event timing, attenuation or spatial-audio setup
has been installed or tested. Preserve existing working Orion audio.

REPRODUCE / EDIT
Run generate_audio.py with Python 3.10+ and NumPy, SciPy and soundfile.
The script also uses ffmpeg, when present, to export the MP3 preview.
The generator is deterministic. Its numbers are artistic audio parameters,
not specifications of the aircraft, missile, engine or explosive system.
asset_manifest.json lists file durations, channels, levels and purposes.
