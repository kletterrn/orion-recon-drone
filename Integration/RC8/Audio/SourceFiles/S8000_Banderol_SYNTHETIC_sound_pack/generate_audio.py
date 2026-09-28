"""Original procedural game-audio sketches, NOT S8000 field recordings.

Requirements: Python 3.10+, numpy, scipy, soundfile; ffmpeg for MP3.
All numerical choices are artistic sound-design settings, not measured
engine, flight, or explosive specifications.
"""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
OUT = Path(__file__).resolve().parent
RNG = np.random.default_rng(80002026)
TAU = 2 * np.pi


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))


def unit(x: np.ndarray) -> np.ndarray:
    return x / max(rms(x), 1e-10)


def band_noise(n: int, low: float, high: float, rng=None) -> np.ndarray:
    """Periodic filtered noise: cyclic spectrum makes seamless loop layers."""
    rng = RNG if rng is None else rng
    f = np.fft.rfftfreq(n, 1 / SR)
    shape = 1 / np.sqrt(1 + (np.maximum(f, .001) / high) ** 8)
    shape *= 1 / np.sqrt(1 + (low / np.maximum(f, .001)) ** 8)
    shape[0] = 0
    spec = (rng.normal(size=len(f)) + 1j * rng.normal(size=len(f))) * shape
    spec[-1] = spec[-1].real
    return unit(np.fft.irfft(spec, n=n))


def filt(x: np.ndarray, cutoff, kind='lowpass') -> np.ndarray:
    sos = signal.butter(3, cutoff, btype=kind, fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def fade(x: np.ndarray, enter=.04, leave=.12) -> np.ndarray:
    x = x.copy()
    if enter:
        m = min(round(enter * SR), len(x))
        env = np.sin(np.linspace(0, np.pi/2, m)) ** 2
        x[:m] *= env if x.ndim == 1 else env[:, None]
    if leave:
        m = min(round(leave * SR), len(x))
        env = np.cos(np.linspace(0, np.pi/2, m)) ** 2
        x[-m:] *= env if x.ndim == 1 else env[:, None]
    return x


def stereo(x: np.ndarray, pan=0.0) -> np.ndarray:
    if x.ndim == 2:
        return x.copy()
    pan = np.asarray(pan)
    theta = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.column_stack((x * np.cos(theta), x * np.sin(theta)))


def gain_to(x: np.ndarray, target_rms=.17, ceiling=.76) -> np.ndarray:
    y = x * (target_rms / max(rms(x), 1e-10))
    peak = float(np.max(np.abs(y)))
    if peak > ceiling:
        y *= ceiling / peak
    return y


def flight_loop(duration=12., high=False) -> np.ndarray:
    """Dry, periodic turbine/air-rush texture. No baked Doppler/reverb."""
    n = round(duration * SR)
    t = np.arange(n) / SR
    freq = 965. if not high else 1095.
    freq = round(freq * duration) / duration
    # All oscillation/modulation cycles close at the loop boundary.
    phase = TAU * freq * t + .12 * np.sin(TAU * 7 * t / duration)
    phase += .045 * np.sin(TAU * 23 * t / duration)
    whine = np.zeros(n)
    for multiple, amplitude in [(1., .24), (2., .115), (3., .05), (4., .022)]:
        whine += amplitude * np.sin(multiple * phase + .17 * multiple)
    # Nearby narrow-band turbulence avoids an overly pure electronic whistle.
    center = 3000 if high else 2670
    turbine_air = band_noise(n, center - 420, center + 460)
    body = band_noise(n, 65, 920)
    roar = band_noise(n, 250, 5200 if high else 4400)
    air = band_noise(n, 1600, 12500)
    flutter = 1 + .06*np.sin(TAU*11*t/duration) + .035*np.sin(TAU*29*t/duration)
    x = (.31*body + .47*roar + .15*air + .08*turbine_air) * flutter + whine
    x = .65 * np.tanh(x / .65)
    # A smooth periodic high-pass in the frequency domain, preserving seam.
    f = np.fft.rfftfreq(n, 1/SR)
    hp = 1 / np.sqrt(1 + (32 / np.maximum(f,.001))**8)
    hp[0] = 0
    x = np.fft.irfft(np.fft.rfft(x) * hp, n)
    return gain_to(x, .18 if high else .155)


def spoolup(duration=7.) -> np.ndarray:
    n = round(duration*SR)
    t = np.arange(n)/SR
    p = np.clip((t-.2)/5.4, 0, 1)
    smooth = p*p*(3-2*p)
    hz = 160 + 805*smooth
    phase = TAU*np.cumsum(hz)/SR
    motor = .12*np.sin(phase) + .065*np.sin(phase*2) + .025*np.sin(phase*3)
    air = band_noise(n, 180, 8800)
    body = band_noise(n, 55, 850)
    amplitude = .03 + .65*smooth
    x = amplitude * (motor + .32*air + .20*body)
    x = np.tanh(x*1.5)
    return gain_to(fade(x,.3,.25), .12, .66)


def flyby(loop: np.ndarray, duration=11., distant=False) -> np.ndarray:
    """Artistic pitch/time sweep, level envelope, EQ and stereo motion."""
    n = round(duration*SR)
    t = np.arange(n)/SR
    midpoint = duration*.45
    tau = 1.45 if distant else .61
    axis = (t-midpoint)/tau
    radial = axis/np.sqrt(1+axis*axis)
    ratio = 1.0 - (.16 if distant else .255)*radial
    pos = np.cumsum(ratio) % len(loop)
    dry = np.interp(pos, np.arange(len(loop)+1), np.r_[loop,loop[0]])
    near = 1/np.sqrt(1+axis*axis)
    low = filt(dry, 1250 if distant else 1750)
    mid = filt(dry, 4200 if distant else 7500)
    color = low + (mid-low)*near
    if not distant:
        color += .12*(dry-mid)*near
    air = band_noise(n, 450, 9500)
    whoosh = .04*air*np.exp(-.5*(axis/1.05)**2)
    level = (.92 if distant else 1.25)*near**(.85 if distant else 1.1)
    # Slightly stronger receding exhaust as a sound-design choice.
    level *= 1 + .15*(1+np.tanh(axis))
    mono = (color*level + whoosh)
    pan = (.65 if distant else .94)*np.tanh(axis*.6)
    return fade(stereo(mono,pan), .65, 1.8)


def impact(duration=7., seed=73) -> np.ndarray:
    """Generic designed impact/explosion. Not modelled to a real warhead."""
    rng = np.random.default_rng(seed)
    n = round(duration*SR)
    t = np.arange(n)/SR
    x = np.zeros(n)
    # Broad sharp attack, diffuse mid body and irregular low-end tail.
    crack = band_noise(n, 900, 15000, rng)*(1-np.exp(-t/.0008))*np.exp(-t/.023)
    body = band_noise(n, 85, 2200, rng)*(1-np.exp(-t/.002))*np.exp(-t/.30)
    low = band_noise(n, 28, 230, rng)*(1-np.exp(-t/.012))*np.exp(-t/.85)
    growl = band_noise(n, 45, 470, rng)*(1-np.exp(-t/.065))*np.exp(-t/1.2)
    air = band_noise(n, 450, 7200, rng)*(1-np.exp(-t/.012))*np.exp(-t/.16)
    x = .52*crack + .59*body + .42*low + .16*growl + .16*air
    # Broad, irregular early reflections instead of rhythmic movie booms.
    core = x.copy()
    for delay, g in [(.061,.16),(.127,.12),(.209,.10),(.353,.07)]:
        k = round(delay*SR)
        x[k:] += g*filt(core, 1500)[:-k]
    # Subtle crumbling impacts, not additional explosions.
    for when in rng.uniform(.16,1.8,14):
        length = .015+rng.uniform(0,.075)
        m = round(length*SR)
        local_t = np.arange(m)/SR
        grain = band_noise(m,180,3500,rng)*np.exp(-local_t/(length/4))
        start = round(when*SR)
        gain = .025*rng.uniform(.25,1.)*np.exp(-when/1.3)
        x[start:start+m] += gain*grain[:max(0,min(m,n-start))]
    x = np.tanh(x*1.05)
    x = filt(x, 27, 'highpass')
    return fade(x, .0005, 1.4)


def debris(duration=5.) -> np.ndarray:
    n = round(duration*SR)
    t = np.arange(n)/SR
    rng = np.random.default_rng(8004)
    x = .035*band_noise(n,300,4700,rng)*(1-np.exp(-t/.05))*np.exp(-t/.65)
    for when in np.sort(rng.uniform(.02,3.3,35)):
        length = rng.uniform(.012,.075)
        m = round(length*SR)
        lt = np.arange(m)/SR
        y = band_noise(m, 250, rng.uniform(1700,6000),rng)
        y *= (1-np.exp(-lt/.0006))*np.exp(-lt/(length/5))
        k = round(when*SR)
        x[k:k+m] += rng.uniform(.018,.06)*np.exp(-when/1.4)*y
    return fade(x, .005, 1)


def distant_impact(near: np.ndarray, duration=10.) -> np.ndarray:
    n = round(duration*SR)
    t = np.arange(n)/SR
    out = np.zeros(n)
    low = filt(near, 720)
    out[:len(low)] += .75*low
    # Diffuse open-air tail: not a measured distance/propagation model.
    diffuse = band_noise(n, 35, 550)
    env = (1-np.exp(-t/.04))*np.exp(-t/1.1)
    out += .065*diffuse*env
    for delay,g in [(.17,.2),(.39,.15),(.78,.09),(1.13,.04)]:
        k = round(delay*SR)
        m = min(len(low), n-k)
        out[k:k+m] += g*low[:m]
    return fade(out,.007,2.)


ASSETS = []


def save(name: str, audio: np.ndarray, use: str, loop=False) -> np.ndarray:
    if not np.isfinite(audio).all():
        raise ValueError(f'Nonfinite samples in {name}')
    peak = float(np.abs(audio).max())
    if peak >= .89:
        audio = audio * .86/peak
    path = OUT / name
    sf.write(path, audio, SR, subtype='PCM_16')
    item = dict(file=name, seconds=round(len(audio)/SR,3),
                channels=1 if audio.ndim==1 else audio.shape[1],
                sample_rate=SR, bit_depth=16, loop=loop, purpose=use,
                peak_dbfs=round(20*np.log10(max(np.abs(audio).max(),1e-12)),2),
                rms_dbfs=round(20*np.log10(max(rms(audio),1e-12)),2))
    if loop:
        item['loop_join_jump'] = round(float(abs(audio[0]-audio[-1])),6)
    ASSETS.append(item)
    return audio


def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    flight = save('02_flight_engine_LOOP_mono_SYNTHETIC.wav',flight_loop(),
                  'Dry continuous engine emitter, no baked movement',True)
    high = save('03_flight_engine_high_LOOP_mono_SYNTHETIC.wav',flight_loop(high=True),
                'Brighter alternative engine texture; not a measured thrust mode',True)
    start = save('01_turbine_spoolup_mono_SYNTHETIC.wav',spoolup(),
                 'Illustrative rising turbine sound; not authentic launch timing')
    closepass = save('04_flyby_close_stereo_SYNTHETIC.wav',flyby(high),
                     'Rendered left-to-right cinematic flyby; movement is baked in')
    farpass = save('05_flyby_distant_stereo_SYNTHETIC.wav',flyby(flight,12,True)*.64,
                   'Rendered softer, filtered distant pass')
    near = save('07_impact_close_mono_SYNTHETIC.wav',impact(),
                'Generic short attack, body and decay; no real yield or signature')
    far = save('08_impact_distant_mono_SYNTHETIC.wav',distant_impact(near),
               'Generic muffled explosion with a rolling tail')
    bits = save('09_debris_tail_mono_SYNTHETIC.wav',debris(),
                'Separate restrained rubble/debris sweetener')

    # Incoming sequence is an edited illustration, not a flight simulation.
    n = 13*SR
    incoming = np.zeros((n,2))
    t = np.arange(6*SR)/SR
    p = (t/6)**1.9
    rate = 1.12+.08*p
    idx = np.cumsum(rate)%len(high)
    dry = np.interp(idx,np.arange(len(high)+1),np.r_[high,high[0]])
    lo = filt(dry,1400)
    approach = (lo+(dry-lo)*p)*(.06+.68*p)
    approach = fade(approach,.5,.008)
    incoming[:len(approach)] += stereo(approach, -.12)
    k = 6*SR
    incoming[k:k+len(near)] += stereo(near)
    incoming[k:k+len(bits)] += stereo(bits, .25)*.55
    incoming = save('06_incoming_and_impact_stereo_SYNTHETIC.wav',incoming,
                    'Edited six-second approach plus generic impact; preview use')

    # A concise showcase. One continuous master gain preserves dynamic range.
    demo = np.zeros((51*SR,2))
    chapters = []
    def put(at, x, label, gain=1.):
        k = round(at*SR)
        y = stereo(x)*gain
        demo[k:k+len(y)] += y
        chapters.append(dict(start_seconds=at,end_seconds=at+len(y)/SR,label=label))
    put(0,start,'Illustrative turbine spool-up',.88)
    put(7,fade(flight[:6*SR],.18,.35),'Steady engine sound',.95)
    put(14,closepass,'Close stereo flyby',1.)
    put(26,incoming,'Incoming pass; generic impact at 00:32',.80)
    put(40,far,'Distant generic impact',.80)
    demo = fade(demo,.025,.25)
    peak = float(np.max(np.abs(demo)))
    demo *= min(1., .78/max(peak,1e-10))
    sf.write(OUT/'Banderol_STYLE_SYNTHETIC_preview.wav',demo,SR,subtype='PCM_16')
    mp3 = OUT/'Banderol_STYLE_SYNTHETIC_preview.mp3'
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        subprocess.run([ffmpeg,'-y','-hide_banner','-loglevel','error',
            '-i',str(OUT/'Banderol_STYLE_SYNTHETIC_preview.wav'),
            '-codec:a','libmp3lame','-b:a','192k',
            '-metadata','title=S8000 Banderol STYLE - SYNTHETIC sound design',
            '-metadata','comment=Not a real recording; original procedural game audio',
            str(mp3)],check=True)
    data = dict(title='S8000 Banderol-inspired SYNTHETIC game-audio sketches',
        authenticity='Not field recordings. Engine, timing, movement and impacts are artistic approximations.',
        assets=ASSETS, preview_seconds=len(demo)/SR, preview_chapters=chapters)
    (OUT/'asset_manifest.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(data,indent=2))


if __name__=='__main__':
    main()
