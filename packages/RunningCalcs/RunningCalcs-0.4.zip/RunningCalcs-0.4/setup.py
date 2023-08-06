import textwrap

from distutils.core import setup
setup(
    name='RunningCalcs',
    version='0.4',
    description='A library for executing running calculations',
    author='Tal Einat',
    author_email='taleinat@gmail.com',
    url='http://bitbucket.org/taleinat/runningcalcs/',
    py_modules=['RunningCalcs'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Natural Language :: English',
    ],
    long_description=textwrap.dedent("""\
        ============
        RunningCalcs
        ============
        --------------------------------------------
        A library for executing running calculations
        --------------------------------------------
        
        Introduction
        ============
        
        Instances of the ``RunnincCalc`` classes in this library can be fed one input value at a time. This allows running several calculations in a single pass over an iterator. This isn't possible with the built-in variants of most calculations, such as ``max()`` and ``heapq.nlargest()``.
        
        ``RunningCalc`` instances can be fed values directly, for example::
        
            mean_rc, stddev_rc = RunningMean(), RunningStdDev()
            for x in values:
                mean_rc.feed(x)
                stddev_rc.feed(x)
            mean, stddev = mean_rc.value, stddev_rc.value
        
        Additionally, the ``apply_in_parallel()`` function is supplied, which makes performing several calculations in parallel easy (and fast!). For example::
        
            mean, stddev = apply_in_parallel([RunningMean(), RunningStdDev()], values)
            five_smallest, five_largest = apply_in_parallel([RunningNSmallest(5), RunningNLargest(5)], values)
        
        Optimizations
        =============
        In addition to the basic ``feed()`` method, some ``RunningCalc`` classes also implement an optimized ``feedMultiple()`` method, which accepts a sequence of values to be processed. This allows values to be processed in chunks, allowing for faster processing in many cases.
        
        The ``apply_in_parallel()`` function automatically splits the given iterable of input values into chunks (chunk size can be controlled via the ``chunk_size`` keyword argument). Therefore using ``apply_in_parallel()`` is both fast and easy.
        
        Writing Your Own RunningCalc Class
        ==================================
        1. sub-class ``RunningCalc``
        2. implement the ``__init__()`` and ``feed()`` methods
        3. make the calculation output value accessible via the ``value`` attribute
        4. optionally implement an optimized ``feedMultiple()`` method
           Note: the ``RunningCalc`` base class includes a default naive implementation of ``feedMultiple()``
        """),
    )
