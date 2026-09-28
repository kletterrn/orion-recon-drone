"""Original synthetic camera microphone engine samples and terminal cues."""
import math, wave, struct, hashlib, random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Sounds/ORD'; OUT.mkdir(parents=True,exist_ok=True)
def write(name,seconds,freq,level):
    rate=48000; samples=[]; rng=random.Random(612)
    bands=[(rng.randrange(180,1900),rng.random()*math.tau) for _ in range(18)]
    for i in range(int(seconds*rate)):
        t=i/rate
        if 'Engine' in name:
            # Original piston/propeller design: combustion harmonics, blade
            # pulses, mechanical chatter and periodic broadband airflow.
            # Integer frequencies and periodic modulation make an eight-second loop.
            cruise='Cruise' in name
            firing=148 if cruise else 52
            prop=78 if cruise else 32
            phase=math.tau*firing*t+.12*math.sin(math.tau*.5*t)
            combustion=sum(math.sin(h*phase+.17*h)/(h**1.25) for h in range(1,10))
            blade=math.sin(math.tau*prop*t)+.33*math.sin(math.tau*prop*2*t)
            airflow=sum(math.sin(math.tau*f*t+p) for f,p in bands)/math.sqrt(len(bands))
            pulse=.72+.28*math.sin(math.tau*prop*t)**2
            value=math.tanh(.58*combustion+.30*blade+.15*airflow*pulse)
            value*=.95+.05*math.sin(math.tau*.25*t)
            # Very short end fades prevent clicks when the engine restarts a WAV.
            edge=min(1,t/.008,(seconds-t-1/rate)/.008)
            value*=math.sin(max(0,edge)*math.pi/2)**2
        else:
            value=math.sin(2*math.pi*freq*t)*math.sin(math.pi*t/seconds)**2
        samples.append(struct.pack('<h',int(max(-1,min(1,value*level))*32767)))
    with wave.open(str(OUT/(name+'.wav')),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(b''.join(samples))
    guid=hashlib.sha1(name.encode()).hexdigest()[:16].upper()
    (OUT/(name+'.wav.meta')).write_text('MetaFileClass {\n Name "{'+guid+'}Sounds/ORD/'+name+'.wav"\n Configurations {\n  WAVResourceClass PC {}\n  WAVResourceClass HEADLESS : PC {}\n }\n}\n')
    print(name,guid)
write('ORD_EngineIdle',8,52,.20)
write('ORD_EngineCruise',8,148,.24)
write('ORD_LinkOpen',.18,880,.16)
write('ORD_LinkClose',.18,440,.16)
