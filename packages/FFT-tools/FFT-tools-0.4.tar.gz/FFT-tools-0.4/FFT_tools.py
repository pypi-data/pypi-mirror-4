# Copyright (C) 2008-2012  W. Trevor King
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Wrap Numpy's fft module to reduce clutter.

Provides a unitary discrete FFT and a windowed version based on
numpy.fft.rfft.

Create some fake data:

>>> import numpy
>>> data = numpy.random.rand(10)
>>> frequency = 1

Main entry functions:

>>> rfft = unitary_rfft(data, freq=frequency)
>>> psd = power_spectrum(data, freq=frequency)
>>> upsd = unitary_power_spectrum(data, freq=frequency)
>>> apsd = avg_power_spectrum(data, freq=frequency, chunk_size=2048,
...     overlap=True, window=window_hann)
>>> aupsd = unitary_avg_power_spectrum(data, freq=frequency, chunk_size=2048,
...     overlap=True, window=window_hann)
"""

import numpy as _numpy


__version__ = '0.4'

# Display time- and freq-space plots of the test transforms if True
TEST_PLOTS = False


def floor_pow_of_two(num):
    "Round num down to the closest exact a power of two."
    lnum = _numpy.log2(num)
    if int(lnum) != lnum:
        num = 2**_numpy.floor(lnum)
    return num


def round_pow_of_two(num):
    "Round num to the closest exact a power of two on a log scale."
    lnum = _numpy.log2(num)
    if int(lnum) != lnum:
        num = 2**_numpy.round(lnum)
    return num


def ceil_pow_of_two(num):
    "Round num up to the closest exact a power of two."
    lnum = _numpy.log2(num)
    if int(lnum) != lnum:
        num = 2**_numpy.ceil(lnum)
    return num


def _test_rfft(xs, Xs):
    # Numpy's FFT algoritm returns
    #          n-1
    #   X[k] = SUM x[m] exp (-j 2pi km /n)
    #          m=0
    # (see http://www.tramy.us/numpybook.pdf)
    j = _numpy.complex(0, 1)
    n = len(xs)
    Xa = []
    for k in range(n):
        Xa.append(sum([x * _numpy.exp(-j * 2 * _numpy.pi * k * m / n)
                       for x,m in zip(xs, range(n))]))
        if k < len(Xs):
            if (Xs[k] - Xa[k]) / _numpy.abs(Xa[k]) >= 1e-6:
                raise ValueError(
                    ('rfft mismatch on element {}: {} != {}, relative error {}'
                     ).format(
                        k, Xs[k], Xa[k], (Xs[k] - Xa[k]) / _numpy.abs(Xa[k])))
    # Which should satisfy the discrete form of Parseval's theorem
    #   n-1               n-1
    #   SUM |x_m|^2 = 1/n SUM |X_k|^2.
    #   m=0               k=0
    timeSum = sum([_numpy.abs(x)**2 for x in xs])
    freqSum = sum([_numpy.abs(X)**2 for X in Xa])
    if _numpy.abs(freqSum / _numpy.float(n) - timeSum) / timeSum >= 1e-6:
        raise ValueError(
            "Mismatch on Parseval's, {} != 1/{} * {}".format(
                timeSum, n, freqSum))


def _test_rfft_suite():
    print('Test numpy rfft definition')
    xs = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1]
    _test_rfft(xs, _numpy.fft.rfft(xs))


def unitary_rfft(data, freq=1.0):
    """Compute the Fourier transform of real data.

    Unitary (preserves power [Parseval's theorem]).

    If the units on your data are Volts,
    and your sampling frequency is in Hz,
    then freq_axis will be in Hz,
    and trans will be in Volts.
    """
    nsamps = floor_pow_of_two(len(data))
    # Which should satisfy the discrete form of Parseval's theorem
    #   n-1               n-1
    #   SUM |x_m|^2 = 1/n SUM |X_k|^2.
    #   m=0               k=0
    # However, we want our FFT to satisfy the continuous Parseval eqn
    #   int_{-infty}^{infty} |x(t)|^2 dt = int_{-infty}^{infty} |X(f)|^2 df
    # which has the discrete form
    #   n-1              n-1
    #   SUM |x_m|^2 dt = SUM |X'_k|^2 df
    #   m=0              k=0
    # with X'_k = AX, this gives us
    #   n-1                     n-1
    #   SUM |x_m|^2 = A^2 df/dt SUM |X'_k|^2
    #   m=0                     k=0
    # so we see
    #   A^2 df/dt = 1/n
    #   A^2 = 1/n dt/df
    # From Numerical Recipes (http://www.fizyka.umk.pl/nrbook/bookcpdf.html),
    # Section 12.1, we see that for a sampling rate dt, the maximum frequency
    # f_c in the transformed data is the Nyquist frequency (12.1.2)
    #   f_c = 1/2dt
    # and the points are spaced out by (12.1.5)
    #   df = 1/ndt
    # so
    #   dt = 1/ndf
    #   dt/df = 1/ndf^2
    #   A^2 = 1/n^2df^2
    #   A = 1/ndf = ndt/n = dt
    # so we can convert the Numpy transformed data to match our unitary
    # continuous transformed data with (also NR 12.1.8)
    #   X'_k = dtX = X / <sampling freq>
    trans = _numpy.fft.rfft(data[0:nsamps]) / _numpy.float(freq)
    freq_axis = _numpy.linspace(0, freq / 2, nsamps / 2 + 1)
    return (freq_axis, trans)


def _test_unitary_rfft_parsevals(xs, freq, freqs, Xs):
    # Which should satisfy the discretized integral form of Parseval's theorem
    #   n-1              n-1
    #   SUM |x_m|^2 dt = SUM |X_k|^2 df
    #   m=0              k=0
    dt = 1.0 / freq
    df = freqs[1] - freqs[0]
    if df - 1 / (len(xs) * dt * df) >= 1e-6:
        raise ValueError(
            'Mismatch in spacing, {} != 1/({}*{})'.format(df, len(xs), dt))
    Xa = list(Xs)
    for k in range(len(Xs) - 1, 1, -1):
        Xa.append(Xa[k])
    if len(xs) != len(Xa):
        raise ValueError('Length mismatch {} != {}'.format(len(xs), len(Xa)))
    lhs = sum([_numpy.abs(x)**2 for x in xs]) * dt
    rhs = sum([_numpy.abs(X)**2 for X in Xa]) * df
    if _numpy.abs(lhs - rhs) / lhs >= 1e-4:
        raise ValueError("Mismatch on Parseval's, {} != {}".format(lhs, rhs))


def _test_unitary_rfft_parsevals_suite():
    print("Test unitary rfft on Parseval's theorem")
    xs = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1]
    dt = _numpy.pi
    freqs,Xs = unitary_rfft(xs, 1.0 / dt)
    _test_unitary_rfft_parsevals(xs, 1.0 / dt, freqs, Xs)


def _rect(t):
    if _numpy.abs(t) < 0.5:
        return 1
    else:
        return 0


def _test_unitary_rfft_rect(
    a=1.0, time_shift=5.0, samp_freq=25.6, samples=256):
    "Show fft(rect(at)) = 1/abs(a) * _numpy.sinc(f/a)"
    samp_freq = _numpy.float(samp_freq)
    a = _numpy.float(a)

    x = _numpy.zeros((samples,), dtype=_numpy.float)
    dt = 1.0 / samp_freq
    for i in range(samples):
        t = i * dt
        x[i] = _rect(a * (t - time_shift))
    freq_axis, X = unitary_rfft(x, samp_freq)
    #_test_unitary_rfft_parsevals(x, samp_freq, freq_axis, X)

    # remove the phase due to our time shift
    j = _numpy.complex(0.0, 1.0)  # sqrt(-1)
    for i in range(len(freq_axis)):
        f = freq_axis[i]
        inverse_phase_shift = _numpy.exp(j * 2.0 * _numpy.pi * time_shift * f)
        X[i] *= inverse_phase_shift

    expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
    # normalized sinc(x) = sin(pi x)/(pi x)
    # so sinc(0.5) = sin(pi/2)/(pi/2) = 2/pi
    if _numpy.sinc(0.5) != 2.0 / _numpy.pi:
        raise ValueError('abnormal sinc()')
    for i in range(len(freq_axis)):
        f = freq_axis[i]
        expected[i] = 1.0 / _numpy.abs(a) * _numpy.sinc(f / a)

    if TEST_PLOTS:
        figure = _pyplot.figure()
        time_axes = figure.add_subplot(2, 1, 1)
        time_axes.plot(_numpy.arange(0, dt * samples, dt), x)
        time_axes.set_title('time series')
        freq_axes = figure.add_subplot(2, 1, 2)
        freq_axes.plot(freq_axis, X.real, 'r.')
        freq_axes.plot(freq_axis, X.imag, 'g.')
        freq_axes.plot(freq_axis, expected, 'b-')
        freq_axes.set_title('freq series')


def _test_unitary_rfft_rect_suite():
    print('Test unitary FFTs on variously shaped rectangular functions')
    _test_unitary_rfft_rect(a=0.5)
    _test_unitary_rfft_rect(a=2.0)
    _test_unitary_rfft_rect(a=0.7, samp_freq=50, samples=512)
    _test_unitary_rfft_rect(a=3.0, samp_freq=60, samples=1024)


def _gaussian(a, t):
    return _numpy.exp(-a * t**2)


def _test_unitary_rfft_gaussian(
    a=1.0, time_shift=5.0, samp_freq=25.6, samples=256):
    "Show fft(rect(at)) = 1/abs(a) * sinc(f/a)"
    samp_freq = _numpy.float(samp_freq)
    a = _numpy.float(a)

    x = _numpy.zeros((samples,), dtype=_numpy.float)
    dt = 1.0 / samp_freq
    for i in range(samples):
        t = i * dt
        x[i] = _gaussian(a, (t - time_shift))
    freq_axis, X = unitary_rfft(x, samp_freq)
    #_test_unitary_rfft_parsevals(x, samp_freq, freq_axis, X)

    # remove the phase due to our time shift
    j = _numpy.complex(0.0, 1.0)  # sqrt(-1)
    for i in range(len(freq_axis)):
        f = freq_axis[i]
        inverse_phase_shift = _numpy.exp(j * 2.0 * _numpy.pi * time_shift * f)
        X[i] *= inverse_phase_shift

    expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
    for i in range(len(freq_axis)):
        f = freq_axis[i]
        # see Wikipedia, or do the integral yourself.
        expected[i] = _numpy.sqrt(_numpy.pi / a) * _gaussian(
            1.0 / a, _numpy.pi * f)

    if TEST_PLOTS:
        figure = _pyplot.figure()
        time_axes = figure.add_subplot(2, 1, 1)
        time_axes.plot(_numpy.arange(0, dt * samples, dt), x)
        time_axes.set_title('time series')
        freq_axes = figure.add_subplot(2, 1, 2)
        freq_axes.plot(freq_axis, X.real, 'r.')
        freq_axes.plot(freq_axis, X.imag, 'g.')
        freq_axes.plot(freq_axis, expected, 'b-')
        freq_axes.set_title('freq series')


def _test_unitary_rfft_gaussian_suite():
    print("Test unitary FFTs on variously shaped gaussian functions")
    _test_unitary_rfft_gaussian(a=0.5)
    _test_unitary_rfft_gaussian(a=2.0)
    _test_unitary_rfft_gaussian(a=0.7, samp_freq=50, samples=512)
    _test_unitary_rfft_gaussian(a=3.0, samp_freq=60, samples=1024)


def power_spectrum(data, freq=1.0):
    """Compute the power spectrum of DATA taken with a sampling frequency FREQ.

    DATA must be real (not complex).
    Returns a tuple of two arrays, (freq_axis, power), suitable for plotting.
    If the number of samples in data is not an integer power of two,
    the FFT ignores some of the later points.
    """
    nsamps = floor_pow_of_two(len(data))

    freq_axis = _numpy.linspace(0, freq / 2, nsamps / 2 + 1)
    # nsamps/2+1 b/c zero-freq and nyqist-freq are both fully real.
    # >>> help(numpy.fft.fftpack.rfft) for Numpy's explaination.
    # See Numerical Recipies for a details.
    trans = _numpy.fft.rfft(data[0:nsamps])
    power = (trans * trans.conj()).real  # we want the square of the amplitude
    return (freq_axis, power)


def unitary_power_spectrum(data, freq=1.0):
    freq_axis,power = power_spectrum(data, freq)
    # One sided power spectral density, so 2|H(f)|**2
    # (see NR 2nd edition 12.0.14, p498)
    #
    # numpy normalizes with 1/N on the inverse transform ifft,
    # so we should normalize the freq-space representation with 1/sqrt(N).
    # But we're using the rfft, where N points are like N/2 complex points,
    # so 1/sqrt(N/2)
    # So the power gets normalized by that twice and we have 2/N
    #
    # On top of this, the FFT assumes a sampling freq of 1 per second,
    # and we want to preserve area under our curves.
    # If our total time T = len(data)/freq is smaller than 1,
    # our df_real = freq/len(data) is bigger that the FFT expects
    # (dt_fft = 1/len(data)),
    # and we need to scale the powers down to conserve area.
    # df_fft * F_fft(f) = df_real *F_real(f)
    # F_real = F_fft(f) * (1/len)/(freq/len) = F_fft(f)*freq
    # So the power gets normalized by *that* twice and we have 2/N * freq**2

    # power per unit time
    # measure x(t) for time T
    # X(f)   = int_0^T x(t) exp(-2 pi ift) dt
    # PSD(f) = 2 |X(f)|**2 / T

    # total_time = len(data)/float(freq)
    # power *= 2.0 / float(freq)**2   /   total_time
    # power *= 2.0 / freq**2   *   freq / len(data)
    power *= 2.0 / (freq * _numpy.float(len(data)))

    return (freq_axis, power)


def _test_unitary_power_spectrum_sin(sin_freq=10, samp_freq=512, samples=1024):
    x = _numpy.zeros((samples,), dtype=_numpy.float)
    samp_freq = _numpy.float(samp_freq)
    for i in range(samples):
        x[i] = _numpy.sin(2.0 * _numpy.pi * (i / samp_freq) * sin_freq)
    freq_axis, power = unitary_power_spectrum(x, samp_freq)
    imax = _numpy.argmax(power)

    expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
    df = samp_freq / _numpy.float(samples)  # df = 1/T, where T = total_time
    i = int(sin_freq / df)
    # average power per unit time is
    #  P = <x(t)**2>
    # average value of sin(t)**2 = 0.5    (b/c sin**2+cos**2 == 1)
    # so average value of (int sin(t)**2 dt) per unit time is 0.5
    #  P = 0.5
    # we spread that power over a frequency bin of width df, sp
    #  P(f0) = 0.5/df
    # where f0 is the sin's frequency
    #
    # or:
    # FFT of sin(2*pi*t*f0) gives
    #  X(f) = 0.5 i (delta(f-f0) - delta(f-f0)),
    # (area under x(t) = 0, area under X(f) = 0)
    # so one sided power spectral density (PSD) per unit time is
    #  P(f) = 2 |X(f)|**2 / T
    #       = 2 * |0.5 delta(f-f0)|**2 / T
    #       = 0.5 * |delta(f-f0)|**2 / T
    # but we're discrete and want the integral of the 'delta' to be 1,
    # so 'delta'*df = 1  --> 'delta' = 1/df, and
    #  P(f) = 0.5 / (df**2 * T)
    #       = 0.5 / df                (T = 1/df)
    expected[i] = 0.5 / df

    print('The power should be a peak at {} Hz of {} ({}, {})'.format(
            sin_freq, expected[i], freq_axis[imax], power[imax]))
    Pexp = P = 0
    for i in range(len(freq_axis)):
        Pexp += expected[i] * df
        P += power[i] * df
    print('The total power should be {} ({})'.format(Pexp, P))

    if TEST_PLOTS:
        figure = _pyplot.figure()
        time_axes = figure.add_subplot(2, 1, 1)
        time_axes.plot(
            _numpy.arange(0, samples / samp_freq, 1.0 / samp_freq), x, 'b-')
        time_axes.set_title('time series')
        freq_axes = figure.add_subplot(2, 1, 2)
        freq_axes.plot(freq_axis, power, 'r.')
        freq_axes.plot(freq_axis, expected, 'b-')
        freq_axes.set_title(
            '{} samples of sin at {} Hz'.format(samples, sin_freq))


def _test_unitary_power_spectrum_sin_suite():
    print('Test unitary power spectrums on variously shaped sin functions')
    _test_unitary_power_spectrum_sin(sin_freq=5, samp_freq=512, samples=1024)
    _test_unitary_power_spectrum_sin(sin_freq=5, samp_freq=512, samples=2048)
    _test_unitary_power_spectrum_sin(sin_freq=5, samp_freq=512, samples=4098)
    _test_unitary_power_spectrum_sin(sin_freq=7, samp_freq=512, samples=1024)
    _test_unitary_power_spectrum_sin(sin_freq=5, samp_freq=1024, samples=2048)
    # with some irrational numbers, to check that I'm not getting lucky
    _test_unitary_power_spectrum_sin(
        sin_freq=_numpy.pi, samp_freq=100 * _numpy.exp(1), samples=1024)
    # test with non-integer number of periods
    _test_unitary_power_spectrum_sin(sin_freq=5, samp_freq=512, samples=256)


def _test_unitary_power_spectrum_delta(amp=1, samp_freq=1, samples=256):
    x = _numpy.zeros((samples,), dtype=_numpy.float)
    samp_freq = _numpy.float(samp_freq)
    x[0] = amp
    freq_axis, power = unitary_power_spectrum(x, samp_freq)

    # power = <x(t)**2> = (amp)**2 * dt/T
    # we spread that power over the entire freq_axis [0,fN], so
    #  P(f)  = (amp)**2 dt / (T fN)
    # where
    #  dt = 1/samp_freq        (sample period)
    #  T  = samples/samp_freq  (total time of data aquisition)
    #  fN = 0.5 samp_freq      (Nyquist frequency)
    # so
    #  P(f) = amp**2 / (samp_freq * samples/samp_freq * 0.5 samp_freq)
    #       = 2 amp**2 / (samp_freq*samples)
    expected_amp = 2.0 * amp**2 / (samp_freq * samples)
    expected = _numpy.ones(
        (len(freq_axis),), dtype=_numpy.float) * expected_amp

    print('The power should be flat at y = {} ({})'.format(
        expected_amp, power[0]))

    if TEST_PLOTS:
        figure = _pyplot.figure()
        time_axes = figure.add_subplot(2, 1, 1)
        time_axes.plot(
            _numpy.arange(0, samples / samp_freq, 1.0 / samp_freq), x, 'b-')
        time_axes.set_title('time series')
        freq_axes = figure.add_subplot(2, 1, 2)
        freq_axes.plot(freq_axis, power, 'r.')
        freq_axes.plot(freq_axis, expected, 'b-')
        freq_axes.set_title('{} samples of delta amp {}'.format(samples, amp))


def _test_unitary_power_spectrum_delta_suite():
    print('Test unitary power spectrums on various delta functions')
    _test_unitary_power_spectrum_delta(amp=1, samp_freq=1.0, samples=1024)
    _test_unitary_power_spectrum_delta(amp=1, samp_freq=1.0, samples=2048)
    # expected = 2*computed
    _test_unitary_power_spectrum_delta(amp=1, samp_freq=0.5, samples=2048)
    # expected = 0.5*computed
    _test_unitary_power_spectrum_delta(amp=1, samp_freq=2.0, samples=2048)
    _test_unitary_power_spectrum_delta(amp=3, samp_freq=1.0, samples=1024)
    _test_unitary_power_spectrum_delta(
        amp=_numpy.pi, samp_freq=_numpy.exp(1), samples=1024)


def _gaussian2(area, mean, std, t):
    "Integral over all time = area (i.e. normalized for area=1)"
    return area / (std * _numpy.sqrt(2.0 * _numpy.pi)) * _numpy.exp(
        -0.5 * ((t-mean)/std)**2)


def _test_unitary_power_spectrum_gaussian(
    area=2.5, mean=5, std=1, samp_freq=10.24, samples=512):
    "Test unitary_power_spectrum() on the gaussian function"
    x = _numpy.zeros((samples,), dtype=_numpy.float)
    mean = _numpy.float(mean)
    for i in range(samples):
        t = i / _numpy.float(samp_freq)
        x[i] = _gaussian2(area, mean, std, t)
    freq_axis, power = unitary_power_spectrum(x, samp_freq)

    # generate the predicted curve
    # by comparing our _gaussian2() form to _gaussian(),
    # we see that the Fourier transform of x(t) has parameters:
    #  std'  = 1/(2 pi std)    (references declaring std' = 1/std are
    #                           converting to angular frequency,
    #                           not frequency like we are)
    #  area' = area/[std sqrt(2*pi)]   (plugging into FT of _gaussian() above)
    #  mean' = 0               (changing the mean in the time-domain just
    #                           changes the phase in the freq-domain)
    # So our power spectral density per unit time is given by
    #  P(f) = 2 |X(f)|**2 / T
    # Where
    #  T  = samples/samp_freq  (total time of data aquisition)
    mean = 0.0
    area = area / (std * _numpy.sqrt(2.0 * _numpy.pi))
    std = 1.0 / (2.0 * _numpy.pi * std)
    expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
    # 1/total_time ( = freq_axis[1]-freq_axis[0] = freq_axis[1])
    df = _numpy.float(samp_freq) / samples
    for i in range(len(freq_axis)):
        f = i * df
        gaus = _gaussian2(area, mean, std, f)
        expected[i] = 2.0 * gaus**2 * samp_freq / samples
    print(('The power should be a half-gaussian, '
           'with a peak at 0 Hz with amplitude {} ({})').format(
            expected[0], power[0]))

    if TEST_PLOTS:
        figure = _pyplot.figure()
        time_axes = figure.add_subplot(2, 1, 1)
        time_axes.plot(
            _numpy.arange(0, samples / samp_freq, 1.0 / samp_freq), x, 'b-')
        time_axes.set_title('time series')
        freq_axes = figure.add_subplot(2, 1, 2)
        freq_axes.plot(freq_axis, power, 'r.')
        freq_axes.plot(freq_axis, expected, 'b-')
        freq_axes.set_title('freq series')


def _test_unitary_power_spectrum_gaussian_suite():
    print('Test unitary power spectrums on various gaussian functions')
    _test_unitary_power_spectrum_gaussian(
        area=1, std=1, samp_freq=10.0, samples=1024)
    _test_unitary_power_spectrum_gaussian(
        area=1, std=2, samp_freq=10.0, samples=1024)
    _test_unitary_power_spectrum_gaussian(
        area=1, std=1, samp_freq=10.0, samples=2048)
    _test_unitary_power_spectrum_gaussian(
        area=1, std=1, samp_freq=20.0, samples=2048)
    _test_unitary_power_spectrum_gaussian(
        area=3, std=1, samp_freq=10.0, samples=1024)
    _test_unitary_power_spectrum_gaussian(
        area=_numpy.pi, std=_numpy.sqrt(2), samp_freq=_numpy.exp(1),
        samples=1024)


def window_hann(length):
    "Returns a Hann window array with length entries"
    win = _numpy.zeros((length,), dtype=_numpy.float)
    for i in range(length):
        win[i] = 0.5 * (
            1.0 - _numpy.cos(2.0 * _numpy.pi * _numpy.float(i) / (length)))
    # avg value of cos over a period is 0
    # so average height of Hann window is 0.5
    return win


def avg_power_spectrum(data, freq=1.0, chunk_size=2048,
                       overlap=True, window=window_hann):
    """Compute the avgerage power spectrum of DATA.

    Taken with a sampling frequency FREQ.

    DATA must be real (not complex) by breaking DATA into chunks.
    The chunks may or may not be overlapping (by setting OVERLAP).
    The chunks are windowed by dotting with WINDOW(CHUNK_SIZE), FFTed,
    and the resulting spectra are averaged together.
    See NR 13.4 for rational.

    Returns a tuple of two arrays, (freq_axis, power), suitable for plotting.
    CHUNK_SIZE should really be a power of 2.
    If the number of samples in DATA is not an integer power of CHUNK_SIZE,
    the FFT ignores some of the later points.
    """
    if chunk_size != floor_pow_of_two(chunk_size):
        raise ValueError(
            'chunk_size {} should be a power of 2'.format(chunk_size))

    nchunks = len(data) // chunk_size  # integer division = implicit floor
    if overlap:
        chunk_step = chunk_size / 2
    else:
        chunk_step = chunk_size

    win = window(chunk_size)  # generate a window of the appropriate size
    freq_axis = _numpy.linspace(0, freq / 2, chunk_size / 2 + 1)
    # nsamps/2+1 b/c zero-freq and nyqist-freq are both fully real.
    # >>> help(numpy.fft.fftpack.rfft) for Numpy's explaination.
    # See Numerical Recipies for a details.
    power = _numpy.zeros((chunk_size / 2 + 1, ), dtype=_numpy.float)
    for i in range(nchunks):
        starti = i * chunk_step
        stopi = starti + chunk_size
        fft_chunk = _numpy.fft.rfft(data[starti:stopi] * win)
        p_chunk = (fft_chunk * fft_chunk.conj()).real
        power += p_chunk.astype(_numpy.float)
    power /= _numpy.float(nchunks)
    return (freq_axis, power)


def unitary_avg_power_spectrum(data, freq=1.0, chunk_size=2048,
                               overlap=True, window=window_hann):
    """Compute the average power spectrum, preserving normalization
    """
    freq_axis,power = avg_power_spectrum(
        data, freq, chunk_size, overlap, window)
    #   2.0 / (freq * chunk_size)       |rfft()|**2 --> unitary_power_spectrum
    # see unitary_power_spectrum()
    power *= 2.0 / (freq * _numpy.float(chunk_size)) * 8.0 / 3
    #             * 8/3  to remove power from windowing
    #  <[x(t)*w(t)]**2> = <x(t)**2 * w(t)**2> ~= <x(t)**2> * <w(t)**2>
    # where the ~= is because the frequency of x(t) >> the frequency of w(t).
    # So our calulated power has and extra <w(t)**2> in it.
    # For the Hann window,
    #   <w(t)**2> = <0.5(1 + 2cos + cos**2)> = 1/4 + 0 + 1/8 = 3/8
    # For low frequency components,
    # where the frequency of x(t) is ~= the frequency of w(t),
    # the normalization is not perfect. ??
    # The normalization approaches perfection as chunk_size -> infinity.
    return (freq_axis, power)


def _test_unitary_avg_power_spectrum_sin(
    sin_freq=10, samp_freq=512, samples=1024, chunk_size=512, overlap=True,
    window=window_hann):
    "Test unitary_avg_power_spectrum() on the sine function"
    x = _numpy.zeros((samples,), dtype=_numpy.float)
    samp_freq = _numpy.float(samp_freq)
    for i in range(samples):
        x[i] = _numpy.sin(2.0 * _numpy.pi * (i / samp_freq) * sin_freq)
    freq_axis, power = unitary_avg_power_spectrum(
        x, samp_freq, chunk_size, overlap, window)
    imax = _numpy.argmax(power)

    expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
    df = samp_freq / _numpy.float(chunk_size)  # df = 1/T, where T = total_time
    i = int(sin_freq / df)
    expected[i] = 0.5 / df  # see _test_unitary_power_spectrum_sin()

    print('The power should peak at {} Hz of {} ({}, {})'.format(
        sin_freq, expected[i], freq_axis[imax], power[imax]))
    Pexp = P = 0
    for i in range(len(freq_axis)):
        Pexp += expected[i] * df
        P += power[i] * df
    print('The total power should be {} ({})'.format(Pexp, P))

    if TEST_PLOTS:
        figure = _pyplot.figure()
        time_axes = figure.add_subplot(2, 1, 1)
        time_axes.plot(
            _numpy.arange(0, samples / samp_freq, 1.0 / samp_freq), x, 'b-')
        time_axes.set_title('time series')
        freq_axes = figure.add_subplot(2, 1, 2)
        freq_axes.plot(freq_axis, power, 'r.')
        freq_axes.plot(freq_axis, expected, 'b-')
        freq_axes.set_title(
            '{} samples of sin at {} Hz'.format(samples, sin_freq))


def _test_unitary_avg_power_spectrum_sin_suite():
    print('Test unitary avg power spectrums on variously shaped sin functions')
    _test_unitary_avg_power_spectrum_sin(
        sin_freq=5, samp_freq=512, samples=1024)
    _test_unitary_avg_power_spectrum_sin(
        sin_freq=5, samp_freq=512, samples=2048)
    _test_unitary_avg_power_spectrum_sin(
        sin_freq=5, samp_freq=512, samples=4098)
    _test_unitary_avg_power_spectrum_sin(
        sin_freq=17, samp_freq=512, samples=1024)
    _test_unitary_avg_power_spectrum_sin(
        sin_freq=5, samp_freq=1024, samples=2048)
    # test long wavelenth sin, so be closer to window frequency
    _test_unitary_avg_power_spectrum_sin(
        sin_freq=1, samp_freq=1024, samples=2048)
    # finally, with some irrational numbers, to check that I'm not
    # getting lucky
    _test_unitary_avg_power_spectrum_sin(
        sin_freq=_numpy.pi,
        samp_freq=100 * _numpy.exp(1),
        samples=1024)


def test():
    _test_rfft_suite()
    _test_unitary_rfft_parsevals_suite()
    _test_unitary_rfft_rect_suite()
    _test_unitary_rfft_gaussian_suite()
    _test_unitary_power_spectrum_sin_suite()
    _test_unitary_power_spectrum_delta_suite()
    _test_unitary_power_spectrum_gaussian_suite()
    _test_unitary_avg_power_spectrum_sin_suite()


if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser('%prog [options]', epilog='Run FFT-tools unit tests.')
    p.add_option('-p', '--plot', dest='plot', action='store_true',
                 help='Display time- and freq-space plots of test transforms.')

    options,args = p.parse_args()

    if options.plot:
        import matplotlib.pyplot as _pyplot
        TEST_PLOTS = True
    test()
    if options.plot:
        _pyplot.show()
