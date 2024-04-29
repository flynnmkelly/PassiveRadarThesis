import numpy as np
import matplotlib.pyplot as plt


def timeshift(inX, tshift):
    "Timeshift a vector by tshift samples (may be a non integer)"

    deltat = 1
    df = 1/len(inX)

    inputf = np.fft.fft(inX)
    f = np.arange(0, (1/deltat), df)
    outputf = inputf * np.exp(-1j*2*np.pi*f*tshift)
    x = np.fft.ifft(outputf)
    return x


def genscenario(N, fs, scenarioNUM):
    # a complex random signal
    nn = np.random.randn(N) + 1j*np.random.randn(N)

    # using sample rate to make a time vector
    t = np.arange(N)/fs

    # select scenario 1 or 2
    if scenarioNUM != 1 and scenarioNUM != 2:
        print("Invalid scenario number")
        return

    # scenario 1: one target at timeshift=-100.5, frequency shift=-100
    if scenarioNUM == 1:
        nn2 = timeshift(nn, -100.5)
        nn2 = nn2 * np.exp(1j * 2 * np.pi * -100 * t)

    # note: nn2 is a timeshifted and frequency shifted version of
    # the first signal

    # Alternative configuration
    # scenario 2: three target scenario
    if scenarioNUM == 2:
        nn2 = timeshift(nn, -20.5)
        nn2 = nn2 * np.exp(1j * 2 * np.pi * -100 * t)

        nn3 = timeshift(nn, -40.5)
        nn3 = nn3 * np.exp(1j * 2 * np.pi * -180 * t)

        nn4 = timeshift(nn, -80.5)
        nn4 = nn4 * np.exp(1j * 2 * np.pi * +100 * t)
        nn2 = nn2 + nn3 + nn4

    return nn, nn2
