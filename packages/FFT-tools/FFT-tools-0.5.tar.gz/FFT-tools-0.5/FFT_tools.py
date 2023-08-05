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

"""Wrap Numpy's :py:mod:`~numpy.fft` module to reduce clutter.

Provides a unitary discrete FFT and a windowed version based on
:py:func:`numpy.fft.rfft`.

Main entry functions:

* :py:func:`unitary_rfft`
* :py:func:`power_spectrum`
* :py:func:`unitary_power_spectrum`
* :py:func:`avg_power_spectrum`
* :py:func:`unitary_avg_power_spectrum`
"""

import logging as _logging
import unittest as _unittest

import numpy as _numpy
try:
    import matplotlib.pyplot as _pyplot
except ImportError as e:
    _pyplot = None
    _pyplot_import_error = e


__version__ = '0.5'


LOG = _logging.getLogger('FFT-tools')
LOG.addHandler(_logging.StreamHandler())
LOG.setLevel(_logging.ERROR)


# Display time- and freq-space plots of the test transforms if True
TEST_PLOTS = False


def floor_pow_of_two(num):
    """Round `num` down to the closest exact a power of two.

    Examples
    --------

    >>> floor_pow_of_two(3)
    2
    >>> floor_pow_of_two(11)
    8
    >>> floor_pow_of_two(15)
    8
    """
    lnum = _numpy.log2(num)
    if int(lnum) != lnum:
        num = 2**_numpy.floor(lnum)
    return int(num)


def round_pow_of_two(num):
    """Round `num` to the closest exact a power of two on a log scale.

    Examples
    --------

    >>> round_pow_of_two(2.9) # Note rounding on *log scale*
    4
    >>> round_pow_of_two(11)
    8
    >>> round_pow_of_two(15)
    16
    """
    lnum = _numpy.log2(num)
    if int(lnum) != lnum:
        num = 2**_numpy.round(lnum)
    return int(num)


def ceil_pow_of_two(num):
    """Round `num` up to the closest exact a power of two.

    Examples
    --------

    >>> ceil_pow_of_two(3)
    4
    >>> ceil_pow_of_two(11)
    16
    >>> ceil_pow_of_two(15)
    16
    """
    lnum = _numpy.log2(num)
    if int(lnum) != lnum:
        num = 2**_numpy.ceil(lnum)
    return int(num)


def unitary_rfft(data, freq=1.0):
    """Compute the unitary Fourier transform of real data.

    Unitary = preserves power [Parseval's theorem].

    Parameters
    ----------
    data : iterable
        Real (not complex) data taken with a sampling frequency `freq`.
    freq : real
        Sampling frequency.

    Returns
    -------
    freq_axis,trans : numpy.ndarray
        Arrays ready for plotting.

    Notes
    -----
    If the units on your data are Volts,
    and your sampling frequency is in Hz,
    then `freq_axis` will be in Hz,
    and `trans` will be in Volts.
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


def power_spectrum(data, freq=1.0):
    """Compute the power spectrum of the time series `data`.

    Parameters
    ----------
    data : iterable
        Real (not complex) data taken with a sampling frequency `freq`.
    freq : real
        Sampling frequency.

    Returns
    -------
    freq_axis,power : numpy.ndarray
        Arrays ready for plotting.

    Notes
    -----
    If the number of samples in `data` is not an integer power of two,
    the FFT ignores some of the later points.

    See Also
    --------
    unitary_power_spectrum,avg_power_spectrum
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
    """Compute the unitary power spectrum of the time series `data`.

    See Also
    --------
    power_spectrum,unitary_avg_power_spectrum
    """
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


def window_hann(length):
    r"""Returns a Hann window array with length entries

    Notes
    -----
    The Hann window with length :math:`L` is defined as

    .. math:: w_i = \frac{1}{2} (1-\cos(2\pi i/L))
    """
    win = _numpy.zeros((length,), dtype=_numpy.float)
    for i in range(length):
        win[i] = 0.5 * (
            1.0 - _numpy.cos(2.0 * _numpy.pi * _numpy.float(i) / (length)))
    # avg value of cos over a period is 0
    # so average height of Hann window is 0.5
    return win


def avg_power_spectrum(data, freq=1.0, chunk_size=2048,
                       overlap=True, window=window_hann):
    """Compute the avgerage power spectrum of `data`.

    Parameters
    ----------
    data : iterable
        Real (not complex) data taken with a sampling frequency `freq`.
    freq : real
        Sampling frequency.
    chunk_size : int
        Number of samples per chunk.  Use a power of two.
    overlap: {True,False}
        If `True`, each chunk overlaps the previous chunk by half its
        length.  Otherwise, the chunks are end-to-end, and not
        overlapping.
    window: iterable
        Weights used to "smooth" the chunks, there is a whole science
        behind windowing, but if you're not trying to squeeze every
        drop of information out of your data, you'll be OK with the
        default Hann window.

    Returns
    -------
    freq_axis,power : numpy.ndarray
        Arrays ready for plotting.

    Notes
    -----
    The average power spectrum is computed by breaking `data` into
    chunks of length `chunk_size`.  These chunks are transformed
    individually into frequency space and then averaged together.

    See Numerical Recipes 2 section 13.4 for a good introduction to
    the theory.

    If the number of samples in `data` is not a multiple of
    `chunk_size`, we ignore the extra points.
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
    """Compute the unitary average power spectrum of `data`.

    See Also
    --------
    avg_power_spectrum,unitary_power_spectrum
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


class TestRFFT (_unittest.TestCase):
    r"""Ensure Numpy's FFT algorithm acts as expected.

    Notes
    -----
    The expected return values are [#dft]_:

    .. math:: X_k = \sum_{m=0}^{n-1} x_m \exp^{-2\pi imk/n}

    .. [#dft] See the *Background information* section of
       :py:mod:`numpy.fft`.
    """
    def run_rfft(self, xs, Xs):
        i = _numpy.complex(0, 1)
        n = len(xs)
        Xa = []
        for k in range(n):
            Xa.append(sum([x * _numpy.exp(-2 * _numpy.pi * i * m * k / n)
                           for x,m in zip(xs, range(n))]))
            if k < len(Xs):
                self.assertAlmostEqual(
                    (Xs[k] - Xa[k]) / _numpy.abs(Xa[k]), 0, 6,
                    ('rfft mismatch on element {}: {} != {}, '
                     'relative error {}').format(
                        k, Xs[k], Xa[k], (Xs[k] - Xa[k]) / _numpy.abs(Xa[k])))
        # Which should satisfy the discrete form of Parseval's theorem
        #   n-1               n-1
        #   SUM |x_m|^2 = 1/n SUM |X_k|^2.
        #   m=0               k=0
        timeSum = sum([_numpy.abs(x)**2 for x in xs])
        freqSum = sum([_numpy.abs(X)**2 for X in Xa])
        self.assertAlmostEqual(
            _numpy.abs(freqSum / _numpy.float(n) - timeSum) / timeSum, 0, 6,
            "Mismatch on Parseval's, {} != 1/{} * {}".format(
                timeSum, n, freqSum))

    def test_rfft(self):
        "Test NumPy's builtin :py:func:`numpy.fft.rfft`"
        xs = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1]
        self.run_rfft(xs, _numpy.fft.rfft(xs))


class TestUnitaryRFFT (_unittest.TestCase):
    """Verify :py:func:`unitary_rfft`.
    """
    def run_parsevals(self, xs, freq, freqs, Xs):
        """Check the discretized integral form of Parseval's theorem

        Notes
        -----
        Which is:

        .. math:: \sum_{m=0}^{n-1} |x_m|^2 dt = \sum_{k=0}^{n-1} |X_k|^2 df
        """
        dt = 1.0 / freq
        df = freqs[1] - freqs[0]
        self.assertAlmostEqual(
            (df - 1 / (len(xs) * dt)) / df, 0, 6,
            'Mismatch in spacing, {} != 1/({}*{})'.format(df, len(xs), dt))
        Xa = list(Xs)
        for k in range(len(Xs) - 1, 1, -1):
            Xa.append(Xa[k])
        self.assertEqual(len(xs), len(Xa))
        lhs = sum([_numpy.abs(x)**2 for x in xs]) * dt
        rhs = sum([_numpy.abs(X)**2 for X in Xa]) * df
        self.assertAlmostEqual(
            _numpy.abs(lhs - rhs) / lhs, 0, 3,
            "Mismatch on Parseval's, {} != {}".format(lhs, rhs))

    def test_parsevals(self):
        "Test unitary rfft on Parseval's theorem"
        xs = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1]
        dt = _numpy.pi
        freqs,Xs = unitary_rfft(xs, 1.0 / dt)
        self.run_parsevals(xs, 1.0 / dt, freqs, Xs)

    def rect(self, t):
        r"""Rectangle function.

        Notes
        -----

        .. math::

            \rect(t) = \begin{cases}
               1& \text{if $|t| < 0.5$}, \\
               0& \text{if $|t| \ge 0.5$}.
                             \end{cases}
        """
        if _numpy.abs(t) < 0.5:
            return 1
        else:
            return 0

    def run_rect(self, a=1.0, time_shift=5.0, samp_freq=25.6, samples=256):
        r"""Test :py:func:`unitary_rfft` on known function :py:meth:`rect`.

        Notes
        -----
        Analytic result:

        .. math:: \rfft(\rect(at)) = 1/|a|\cdot\sinc(f/a)
        """
        samp_freq = _numpy.float(samp_freq)
        a = _numpy.float(a)

        x = _numpy.zeros((samples,), dtype=_numpy.float)
        dt = 1.0 / samp_freq
        for i in range(samples):
            t = i * dt
            x[i] = self.rect(a * (t - time_shift))
        freq_axis,X = unitary_rfft(x, samp_freq)

        # remove the phase due to our time shift
        j = _numpy.complex(0.0, 1.0)  # sqrt(-1)
        for i in range(len(freq_axis)):
            f = freq_axis[i]
            inverse_phase_shift = _numpy.exp(
                j * 2.0 * _numpy.pi * time_shift * f)
            X[i] *= inverse_phase_shift

        expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
        # normalized sinc(x) = sin(pi x)/(pi x)
        # so sinc(0.5) = sin(pi/2)/(pi/2) = 2/pi
        self.assertEqual(_numpy.sinc(0.5), 2.0 / _numpy.pi)
        for i in range(len(freq_axis)):
            f = freq_axis[i]
            expected[i] = 1.0 / _numpy.abs(a) * _numpy.sinc(f / a)

        if TEST_PLOTS:
            if _pyplot is None:
                raise _pyplot_import_error
            figure = _pyplot.figure()
            time_axes = figure.add_subplot(2, 1, 1)
            time_axes.plot(_numpy.arange(0, dt * samples, dt), x)
            time_axes.set_title('time series')
            freq_axes = figure.add_subplot(2, 1, 2)
            freq_axes.plot(freq_axis, X.real, 'r.')
            freq_axes.plot(freq_axis, X.imag, 'g.')
            freq_axes.plot(freq_axis, expected, 'b-')
            freq_axes.set_title('freq series')

    def test_rect(self):
        "Test unitary FFTs on variously shaped rectangular functions."
        self.run_rect(a=0.5)
        self.run_rect(a=2.0)
        self.run_rect(a=0.7, samp_freq=50, samples=512)
        self.run_rect(a=3.0, samp_freq=60, samples=1024)

    def gaussian(self, a, t):
        r"""Gaussian function.

        Notes
        -----

        .. math:: \gaussian(a,t) = \exp^{-at^2}
        """
        return _numpy.exp(-a * t**2)

    def run_gaussian(self, a=1.0, time_shift=5.0, samp_freq=25.6, samples=256):
        r"""Test :py:func:`unitary_rttf` on known function :py:meth:`gaussian`.

        Notes
        -----
        Analytic result:

        .. math::

            \rfft(\gaussian(a,t))
              = \sqrt{\pi/a} \cdot \gaussian(1/a,\pi f)
        """
        samp_freq = _numpy.float(samp_freq)
        a = _numpy.float(a)

        x = _numpy.zeros((samples,), dtype=_numpy.float)
        dt = 1.0 / samp_freq
        for i in range(samples):
            t = i * dt
            x[i] = self.gaussian(a, (t - time_shift))
        freq_axis,X = unitary_rfft(x, samp_freq)

        # remove the phase due to our time shift
        j = _numpy.complex(0.0, 1.0)  # sqrt(-1)
        for i in range(len(freq_axis)):
            f = freq_axis[i]
            inverse_phase_shift = _numpy.exp(
                j * 2.0 * _numpy.pi * time_shift * f)
            X[i] *= inverse_phase_shift

        expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
        for i in range(len(freq_axis)):
            f = freq_axis[i]
            # see Wikipedia, or do the integral yourself.
            expected[i] = _numpy.sqrt(_numpy.pi / a) * self.gaussian(
                1.0 / a, _numpy.pi * f)

        if TEST_PLOTS:
            if _pyplot is None:
                raise _pyplot_import_error
            figure = _pyplot.figure()
            time_axes = figure.add_subplot(2, 1, 1)
            time_axes.plot(_numpy.arange(0, dt * samples, dt), x)
            time_axes.set_title('time series')
            freq_axes = figure.add_subplot(2, 1, 2)
            freq_axes.plot(freq_axis, X.real, 'r.')
            freq_axes.plot(freq_axis, X.imag, 'g.')
            freq_axes.plot(freq_axis, expected, 'b-')
            freq_axes.set_title('freq series')

    def test_gaussian(self):
        "Test unitary FFTs on variously shaped gaussian functions."
        self.run_gaussian(a=0.5)
        self.run_gaussian(a=2.0)
        self.run_gaussian(a=0.7, samp_freq=50, samples=512)
        self.run_gaussian(a=3.0, samp_freq=60, samples=1024)


class TestUnitaryPowerSpectrum (_unittest.TestCase):
    def run_sin(self, sin_freq=10, samp_freq=512, samples=1024):
        x = _numpy.zeros((samples,), dtype=_numpy.float)
        samp_freq = _numpy.float(samp_freq)
        for i in range(samples):
            x[i] = _numpy.sin(2.0 * _numpy.pi * (i / samp_freq) * sin_freq)
        freq_axis,power = unitary_power_spectrum(x, samp_freq)
        imax = _numpy.argmax(power)

        expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
        # df = 1/T, where T = total_time
        df = samp_freq / _numpy.float(samples)
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

        LOG.debug('The power should be a peak at {} Hz of {} ({}, {})'.format(
                sin_freq, expected[i], freq_axis[imax], power[imax]))
        Pexp = P = 0
        for i in range(len(freq_axis)):
            Pexp += expected[i] * df
            P += power[i] * df
        self.assertAlmostEqual(
            _numpy.abs((P - Pexp) / Pexp), 0, 1,
            'The total power should be {} ({})'.format(Pexp, P))

        if TEST_PLOTS:
            if _pyplot is None:
                raise _pyplot_import_error
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

    def test_sin(self):
        "Test unitary power spectrums on variously shaped sin functions"
        self.run_sin(sin_freq=5, samp_freq=512, samples=1024)
        self.run_sin(sin_freq=5, samp_freq=512, samples=2048)
        self.run_sin(sin_freq=5, samp_freq=512, samples=4098)
        self.run_sin(sin_freq=7, samp_freq=512, samples=1024)
        self.run_sin(sin_freq=5, samp_freq=1024, samples=2048)
        # finally, with some irrational numbers, to check that I'm not
        # getting lucky
        self.run_sin(
            sin_freq=_numpy.pi, samp_freq=100 * _numpy.exp(1), samples=1024)
        # test with non-integer number of periods
        self.run_sin(sin_freq=5, samp_freq=512, samples=256)

    def run_delta(self, amp=1, samp_freq=1, samples=256):
        """TODO
        """
        x = _numpy.zeros((samples,), dtype=_numpy.float)
        samp_freq = _numpy.float(samp_freq)
        x[0] = amp
        freq_axis,power = unitary_power_spectrum(x, samp_freq)

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

        self.assertAlmostEqual(
            expected_amp, power[0], 4,
            'The power should be flat at y = {} ({})'.format(
                expected_amp, power[0]))

        if TEST_PLOTS:
            if _pyplot is None:
                raise _pyplot_import_error
            figure = _pyplot.figure()
            time_axes = figure.add_subplot(2, 1, 1)
            time_axes.plot(
                _numpy.arange(0, samples / samp_freq, 1.0 / samp_freq), x, 'b-')
            time_axes.set_title('time series')
            freq_axes = figure.add_subplot(2, 1, 2)
            freq_axes.plot(freq_axis, power, 'r.')
            freq_axes.plot(freq_axis, expected, 'b-')
            freq_axes.set_title('{} samples of delta amp {}'.format(samples, amp))

    def test_delta(self):
        "Test unitary power spectrums on various delta functions"
        self.run_delta(amp=1, samp_freq=1.0, samples=1024)
        self.run_delta(amp=1, samp_freq=1.0, samples=2048)
        # expected = 2*computed
        self.run_delta(amp=1, samp_freq=0.5, samples=2048)
        # expected = 0.5*computed
        self.run_delta(amp=1, samp_freq=2.0, samples=2048)
        self.run_delta(amp=3, samp_freq=1.0, samples=1024)
        self.run_delta(amp=_numpy.pi, samp_freq=_numpy.exp(1), samples=1024)

    def gaussian(self, area, mean, std, t):
        "Integral over all time = area (i.e. normalized for area=1)"
        return area / (std * _numpy.sqrt(2.0 * _numpy.pi)) * _numpy.exp(
            -0.5 * ((t-mean)/std)**2)

    def run_gaussian(self, area=2.5, mean=5, std=1, samp_freq=10.24,
                     samples=512):
        """TODO.
        """
        x = _numpy.zeros((samples,), dtype=_numpy.float)
        mean = _numpy.float(mean)
        for i in range(samples):
            t = i / _numpy.float(samp_freq)
            x[i] = self.gaussian(area, mean, std, t)
        freq_axis,power = unitary_power_spectrum(x, samp_freq)

        # generate the predicted curve by comparing our
        # TestUnitaryPowerSpectrum.gaussian() form to
        # TestUnitaryRFFT.gaussian(),
        # we see that the Fourier transform of x(t) has parameters:
        #  std'  = 1/(2 pi std)    (references declaring std' = 1/std are
        #                           converting to angular frequency,
        #                           not frequency like we are)
        #  area' = area/[std sqrt(2*pi)]   (plugging into FT of
        #                                   TestUnitaryRFFT.gaussian() above)
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
            gaus = self.gaussian(area, mean, std, f)
            expected[i] = 2.0 * gaus**2 * samp_freq / samples
        self.assertAlmostEqual(
            expected[0], power[0], 3,
            ('The power should be a half-gaussian, '
             'with a peak at 0 Hz with amplitude {} ({})').format(
                expected[0], power[0]))

        if TEST_PLOTS:
            if _pyplot is None:
                raise _pyplot_import_error
            figure = _pyplot.figure()
            time_axes = figure.add_subplot(2, 1, 1)
            time_axes.plot(
                _numpy.arange(0, samples / samp_freq, 1.0 / samp_freq),
                x, 'b-')
            time_axes.set_title('time series')
            freq_axes = figure.add_subplot(2, 1, 2)
            freq_axes.plot(freq_axis, power, 'r.')
            freq_axes.plot(freq_axis, expected, 'b-')
            freq_axes.set_title('freq series')

    def test_gaussian(self):
        "Test unitary power spectrums on various gaussian functions"
        for area in [1, _numpy.pi]:
            for std in [1, _numpy.sqrt(2)]:
                for samp_freq in [10.0, _numpy.exp(1)]:
                    for samples in [1024, 2048]:
                        self.run_gaussian(
                            area=area, std=std, samp_freq=samp_freq,
                            samples=samples)


class TestUnitaryAvgPowerSpectrum (_unittest.TestCase):
    def run_sin(self, sin_freq=10, samp_freq=512, samples=1024, chunk_size=512,
                overlap=True, window=window_hann, places=3):
        """TODO
        """
        x = _numpy.zeros((samples,), dtype=_numpy.float)
        samp_freq = _numpy.float(samp_freq)
        for i in range(samples):
            x[i] = _numpy.sin(2.0 * _numpy.pi * (i / samp_freq) * sin_freq)
        freq_axis,power = unitary_avg_power_spectrum(
            x, samp_freq, chunk_size, overlap, window)
        imax = _numpy.argmax(power)

        expected = _numpy.zeros((len(freq_axis),), dtype=_numpy.float)
        # df = 1/T, where T = total_time
        df = samp_freq / _numpy.float(chunk_size)
        i = int(sin_freq / df)
        # see TestUnitaryPowerSpectrum.run_unitary_power_spectrum_sin()
        expected[i] = 0.5 / df

        LOG.debug('The power should peak at {} Hz of {} ({}, {})'.format(
                sin_freq, expected[i], freq_axis[imax], power[imax]))
        Pexp = P = 0
        for i in range(len(freq_axis)):
            Pexp += expected[i] * df
            P += power[i] * df
        self.assertAlmostEqual(
            Pexp, P, places,
            'The total power should be {} ({})'.format(Pexp, P))

        if TEST_PLOTS:
            if _pyplot is None:
                raise _pyplot_import_error
            figure = _pyplot.figure()
            time_axes = figure.add_subplot(2, 1, 1)
            time_axes.plot(
                _numpy.arange(0, samples / samp_freq, 1.0 / samp_freq),
                x, 'b-')
            time_axes.set_title('time series')
            freq_axes = figure.add_subplot(2, 1, 2)
            freq_axes.plot(freq_axis, power, 'r.')
            freq_axes.plot(freq_axis, expected, 'b-')
            freq_axes.set_title(
                '{} samples of sin at {} Hz'.format(samples, sin_freq))

    def test_sin(self):
        "Test unitary avg power spectrums on variously shaped sin functions."
        self.run_sin(sin_freq=5, samp_freq=512, samples=1024)
        self.run_sin(sin_freq=5, samp_freq=512, samples=2048)
        self.run_sin(sin_freq=5, samp_freq=512, samples=4098)
        self.run_sin(sin_freq=17, samp_freq=512, samples=1024)
        self.run_sin(sin_freq=5, samp_freq=1024, samples=2048)
        # test long wavelenth sin, so be closer to window frequency
        self.run_sin(sin_freq=1, samp_freq=1024, samples=2048, places=0)
        # finally, with some irrational numbers, to check that I'm not
        # getting lucky
        self.run_sin(
            sin_freq=_numpy.pi, samp_freq=100 * _numpy.exp(1), samples=1024)
