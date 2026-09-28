"""Original illustrative piston/propeller sound design; NOT a recorded Orion UAV.
All timing, tonal parameters, and operating states are artistic approximations.
"""
from pathlib import Path
import json
import numpy as np
from scipy import signal
import soundfile as sf
import subprocess

ROOT = Path(__file__).resolve().parent
SR = 48000
RNG = np.random.default_rng(9272026)


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x*x*(3.0-2.0*x)


def curve(t, knots, values):
    out = np.full_like(t, values[-1], dtype=np.float64)
    out[t <= knots[0]] = values[0]
    for a, b, va, vb in zip(knots[:-1], knots[1:], values[:-1], values[1:]):
        m = (t >= a) & (t < b)
        out[m] = va + (vb-va)*smoothstep((t[m]-a)/(b-a))
    return out


def noise(n, low=None, high=None):
    x = RNG.normal(size=n)
    if low is not None and high is not None:
        sos = signal.butter(2, [low, high], 'bandpass', fs=SR, output='sos')
    elif high is not None:
        sos = signal.butter(2, high, 'lowpass', fs=SR, output='sos')
    else:
        sos = signal.butter(2, low, 'highpass', fs=SR, output='sos')
    x = signal.sosfilt(sos, x)
    return x / max(np.std(x), 1e-8)


def lowpass(x, f):
    return signal.sosfilt(signal.butter(2, f, 'lowpass', fs=SR, output='sos'), x, axis=0)


def engine(rpm, load):
    n = len(rpm)
    t = np.arange(n)/SR
    # Correlated speed variation keeps the demonstration from sounding like a test tone.
    drift = np.interp(t, np.linspace(0,t[-1],max(3,int(t[-1]*20))),
                      RNG.normal(0, 1, max(3,int(t[-1]*20))))
    fluct = 1 + 0.0045*drift + 0.003*np.sin(2*np.pi*1.35*t)
    crank = np.cumsum(rpm*fluct/(60*SR))
    firing = crank*2
    phase = firing % 1
    # Short exhaust-pressure pulses, with varying cycle strength.
    p = np.exp(-phase*17.5) - 0.34*np.exp(-phase*4.2)
    p -= p.mean()
    cylinder = 1 + 0.11*np.sin(2*np.pi*crank/2 + 0.4) + 0.07*np.sin(2*np.pi*crank)
    exhaust = p*cylinder
    exhaust = signal.sosfilt(signal.butter(2,[45,1900],'bandpass',fs=SR,output='sos'), exhaust)
    exhaust *= 1.8
    # Broadband combustion texture, modulated by the exhaust pulse cycle.
    rasp = noise(n,90,2600)*(0.25+0.75*np.exp(-phase*7.0))
    mechanical = (0.055*np.sin(2*np.pi*crank*6.3+0.3*np.sin(2*np.pi*crank))
                  + 0.035*np.sin(2*np.pi*crank*10.8))*load
    # A two-blade-like propeller layer; numerical values are artistic, not Orion data.
    prop = crank/2.43*2
    blade = np.zeros(n)
    phases = RNG.uniform(-np.pi,np.pi,14)
    for k in range(1,15):
        blade += np.exp(-k/7.0)/(k**0.65)*np.sin(2*np.pi*prop*k+phases[k-1])
    blade /= 2.8
    prop_rush = noise(n,120,3200)*(0.7+0.3*np.sin(2*np.pi*prop))
    rumble = noise(n,35,160)
    x = ((0.26+0.23*load)*exhaust + (0.023+0.055*load)*rasp
         + (0.11+0.33*load)*blade + (0.016+0.042*load)*prop_rush
         + 0.015*rumble + mechanical)
    # Gentle saturation only; avoid a cinematic bass/jet treatment.
    return 0.65*np.tanh(x*1.5)


def fade(x, start=0.015, end=0.05):
    x = x.copy()
    a=min(len(x),round(start*SR)); b=min(len(x),round(end*SR))
    if a:
        x[:a] *= smoothstep(np.arange(a)/max(a-1,1)).reshape((-1,)+(1,)*(x.ndim-1))
    if b:
        x[-b:] *= (1-smoothstep(np.arange(b)/max(b-1,1))).reshape((-1,)+(1,)*(x.ndim-1))
    return x


def save(name, x):
    if not np.all(np.isfinite(x)):
        raise ValueError(f'Nonfinite samples: {name}')
    x = np.asarray(x, dtype=np.float32)
    peak = np.max(np.abs(x))
    if peak > 0.88:
        x *= 0.88/peak
    sf.write(ROOT/name, x, SR, subtype='PCM_16')
    return x


def loop(duration, rpm_value, load_value):
    n=round(duration*SR); c=round(0.3*SR)
    raw=engine(np.full(n+c,rpm_value),np.full(n+c,load_value))
    out=raw[c:].copy()
    w=smoothstep(np.arange(c)/max(c-1,1))
    out[-c:]=(1-w)*raw[n:n+c]+w*raw[:c]
    return out

# Startup: brief cranking, uneven ignition catch, then idle.
t=np.arange(round(7*SR))/SR
rpm=curve(t,[0,0.45,1.55,1.95,2.3,3.1,7],[0,200,270,1100,2350,1900,1950])
load=curve(t,[0,1.6,2.3,3.1,7],[0,0,0.3,0.12,0.12])
run=engine(rpm,load)
run*=curve(t,[0,1.55,1.7,1.95,2.3,7],[0,0,0.32,0.63,1,1])
whinephase=np.cumsum(curve(t,[0,.2,1.7,2.1,7],[280,560,690,200,200])/SR)
starter=(0.07*np.sin(2*np.pi*whinephase)+0.025*np.sin(4*np.pi*whinephase)
         +0.035*noise(len(t),140,1700))*(0.65+0.35*np.sin(2*np.pi*5.8*t)**2)
starter*=curve(t,[0,.1,.2,1.75,1.95,7],[0,0,1,1,0,0])
startup=save('01_startup_ILLUSTRATION.wav',fade(run+starter,end=.055))
idle=save('02_idle_loop_ILLUSTRATION.wav',loop(8,1950,.12))

# Power buildup, sustained higher power. This is not a calibrated takeoff recording.
t=np.arange(round(9*SR))/SR
rpm=curve(t,[0,.7,5.4,9],[1950,1950,5150,5150])
load=curve(t,[0,.7,4.2,9],[.12,.12,.95,.95])
power=save('03_takeoff_power_ILLUSTRATION.wav',fade(engine(rpm,load),end=.06))
cruise=save('04_cruise_loop_ILLUSTRATION.wav',loop(8,4420,.52))

# Separate illustrative stereo flyby, with distance-dependent timbre and Doppler.
dur=12; n=round(dur*SR)
t=np.arange(n)/SR
src=engine(np.full(n,4420),np.full(n,.52))
x=(t-dur/2)*43
r=np.sqrt(x*x+72**2)
arrival=t+(r-r[0])/343
heard=np.interp(t,arrival,src,left=0,right=0)
rhear=np.interp(t,arrival,r)
xhear=np.interp(t,arrival,x)
near=np.clip((72/rhear)**.8,0,1)
heard=lowpass(heard,850)*(1-near)+heard*near
heard*=np.clip((72/rhear)**1.05,0,1)
pan=np.clip(xhear/(np.abs(xhear)+100),-.85,.85)
stereo=np.column_stack([heard*np.sqrt((1-pan)/2),heard*np.sqrt((1+pan)/2)])
flyby=save('05_flyby_stereo_ILLUSTRATION.wav',fade(stereo,start=.6,end=1.1))

# Shutdown: idle, slowing pulses, a brief propeller tail, then silence.
t=np.arange(round(5*SR))/SR
rpm=curve(t,[0,1.35,1.55,2.1,3.4,4,5],[1950,1950,1700,1100,330,0,0])
load=np.full(len(t),.1)
stop=engine(rpm,load)*curve(t,[0,1.5,2.2,3.8,4.1,5],[1,1,.55,.12,0,0])
shutdown=save('06_shutdown_ILLUSTRATION.wav',fade(stop,end=.1))

def stereoize(x):
    return np.column_stack([x,x])*.707 if x.ndim==1 else x

def crossfade(a,b,seconds=.13):
    a=stereoize(a); b=stereoize(b)
    k=round(seconds*SR)
    w=smoothstep(np.arange(k)/max(k-1,1))[:,None]
    return np.concatenate([a[:-k],a[-k:]*(1-w)+b[:k]*w,b[k:]])

# A listening montage. The flyby and shutdown are separate scenes, not one mission.
preview=crossfade(startup,power)
preview=crossfade(preview,fade(cruise[:4*SR],end=.25))
pause=np.zeros((round(.6*SR),2))
preview=np.concatenate([preview,pause,flyby,pause,stereoize(shutdown)])
preview=save('Orion_STYLE_SYNTHETIC_preview.wav',preview)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'Orion_STYLE_SYNTHETIC_preview.wav'),
                '-codec:a','libmp3lame','-b:a','192k',str(ROOT/'Orion_STYLE_SYNTHETIC_preview.mp3')],check=True)

readme='''ORION-STYLE SYNTHETIC AUDIO ILLUSTRATION\n======================================\n\nIMPORTANT: NONE OF THESE FILES IS A RECORDING OF AN ORION DRONE.\nThis is an original, procedurally synthesized piston/propeller sound-design\nmock-up. It has not been matched to verified Orion audio. Do not use it as\nevidence of the actual aircraft's sound, pitch, loudness, startup timing,\npropeller speed, operating parameters, or acoustic signature.\n\nCreated from mathematical waveforms and filtered noise; no third-party\nrecorded audio is included. No music, speech, combat sounds, or UI effects.\n\nFILES\n01_startup_ILLUSTRATION.wav          7 s, mono\n02_idle_loop_ILLUSTRATION.wav        8 s, mono, wrap crossfaded\n03_takeoff_power_ILLUSTRATION.wav    9 s, mono, power buildup\n04_cruise_loop_ILLUSTRATION.wav      8 s, mono, wrap crossfaded\n05_flyby_stereo_ILLUSTRATION.wav    12 s, stereo\n06_shutdown_ILLUSTRATION.wav         5 s, mono\nOrion_STYLE_SYNTHETIC_preview.wav  listening montage\nOrion_STYLE_SYNTHETIC_preview.mp3  compressed listening montage\nbuild_audio.py                    reproducible source\n\nWAV format: 48 kHz, 16-bit PCM.\nThis is source audio, NOT a tested Arma Reforger sound configuration.\n\nPREVIEW TIMELINE (approximately)\n00:00-00:07  Starter, ignition catch, idle\n00:07-00:16  Takeoff-power buildup\n00:16-00:20  Steady cruise\n00:20-00:32  Separate stereo flyby example\n00:33-00:38  Separate shutdown example\n\nThe flyby includes baked movement and Doppler: use the mono cruise source\nfor an in-game moving emitter instead of applying another Doppler effect\nto this stereo preview.\n'''
(ROOT/'README.txt').write_text(readme,encoding='utf-8')
stats=[]
for p in sorted(ROOT.glob('*.wav')):
    y,sr=sf.read(p)
    stats.append({'file':p.name,'seconds':round(len(y)/sr,3),'sample_rate':sr,
                  'channels':1 if y.ndim==1 else y.shape[1],
                  'peak_dbfs':round(20*np.log10(max(np.max(np.abs(y)),1e-10)),2),
                  'rms_dbfs':round(20*np.log10(max(np.sqrt(np.mean(y*y)),1e-10)),2)})
(ROOT/'validation.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(json.dumps(stats,indent=2))
