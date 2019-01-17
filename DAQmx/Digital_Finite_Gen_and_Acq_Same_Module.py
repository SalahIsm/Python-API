import nidaqmx as ni
from nidaqmx.constants import AcquisitionType, TaskMode
import numpy as np
import matplotlib.pyplot as plt
import time

from nidaqmx.constants import (LineGrouping)
from scipy import signal

## Generation ##
fe = 100_000                                                                    # freq d'éch. [Hz]
T  = 0.01                                                                      # duree du signal [s]
t = np.linspace(0, T, int(fe * T))                                              # vecteur temps
f1 = 500                                                                        # freq min [Hz]
f2 = 10 * f1                                                                    # freq max [Hz]
f  = np.linspace(f1, f2, len(t))                                                # vecteur freq
sig = signal.square(f * 2 * np.pi * t)                                          # signal à émettre
sig_E = sig
print(len(sig_E))


for i in range(0,len(sig_E)):
    sig_E[i] = True if (sig_E[i] > 0) else False
sig_E = [bool(sig_E[i]) for i in range(len(sig_E))]                             # float2bool

with ni.Task() as gen_task, ni.Task() as acq_task :
    # Configuration tâche DO
    gen_task.do_channels.add_do_chan("cDAQ2Mod1/port0/line0", line_grouping=LineGrouping.CHAN_PER_LINE)
    gen_task.timing.cfg_samp_clk_timing(fe)
    print(gen_task.timing.samp_clk_rate)
    
    # Configuration tâche DI
    acq_task.di_channels.add_di_chan("cDAQ2Mod1/port0/line4", line_grouping=LineGrouping.CHAN_PER_LINE)
    acq_task.timing.cfg_samp_clk_timing(fe/2)
    print(acq_task.timing.samp_clk_rate)


    # Démarrage des tâches
    acq_task.control(TaskMode.TASK_RESERVE)

    gen_task.write(sig_E)                                                       #Il faut absolument reserver la tâche acq avant d'écrire dans le buffer de la tâche gen

    acq_task.start()
    gen_task.start()

    sig_R = acq_task.read(number_of_samples_per_channel=1000)

    print(len(sig_R))
    

## Visualisation ##
plt.figure()

# Signal Emis
plt.subplot(211)

plt.plot(t * 1000, sig_E)
plt.title("Signal Emis")
plt.xlim(0, T * 1000)
plt.ylim(-0.1, 1.1)
plt.xlabel("t [ms]")
plt.ylabel("Amplitude")
plt.grid()
plt.tight_layout()

# -------------------------------------------------------- #
# Signal Reçu
plt.subplot(212)
plt.plot(t * 1000, sig_R, c='r')
plt.title("Signal Reçu")
plt.xlim(0, T * 1000)
plt.ylim(-0.1, 1.1)
plt.xlabel("t [ms]")
plt.ylabel("Amplitude")
plt.grid()
plt.tight_layout()

plt.show()