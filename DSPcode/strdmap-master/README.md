# Examples on how to process data in a passive radar way.


Passive radar starts with processing data to create a range Doppler map. This is done by correlating a direct channel with a surveillance channel. In some scenarios it is possible to auto-correlate the surveillance channel. This happens because the direct signal is so strong that it is still in the target path as well.


The files include:

* genscenario, generates the scenario which will be used for correlations

* rdmap, is the whole process which includes 3 algorithms

A range Doppler map is a 2D correlation - one in both time and frequency.

# Algorithm description

Algorithm 1 shows that correlation in the frequency domain is the same as the time domain.

Algorithm 2 show a complete correlation in time and frequency. For a live recording this should be done on segments of data. It is important for the integration gain to be large enough to get the detections that are needed.

Algorithm 3 is a an interesting approximation which works well, but is able to calculate the RD map much faster.


