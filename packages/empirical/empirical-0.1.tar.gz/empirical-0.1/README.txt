empirical README
==================

Getting Started
---------------

Check out the examples directory; initial development will focus on getting
these working first.


Getting the latest version
--------------------------

If the pypi releases are not up-to-date enough for your tastes, or if you'd
like to see how the development is moving along, visit
https://bitbucket.org/dhild/empirical


Why does this project exist?
----------------------------

The focus of this project is to create a reduced basis solver for collocation
problems. Initially, the collocation problems will be formulated using the
method of fundamental solutions, but ideally the framework will allow for easy
extension to other collocation formulations as well.

There is an existing solver for a variety of methods using MATLAB codes, called
mpspack. (See the 'Thanks' section for details). The mfs code base is basically
a port of this code to Python.

Since mpspack is available under the GPLv3, there should be no legal issues
with creating a Python version. It should be a benefit to the mathematical
world to make code like this more widely available. Unfortunately, since
this project has no official affiliation with mpspack, or its creators Alex
Barnett and Timo Betcke, it will make it harder to keep up with any updates
or additions to their library. At the time of inception for this library, I
used the 1.31 version of mpspack.

The biggest reason to port mpspack to Python is the fact that Python is
free, and MATLAB is expensive. For my Master's thesis, I need to use their
code, but I also need to run it a huge number of times. While my school does
have MATLAB, I did not find it simple to get MATLAB to run in parallel. This
problem seems to stem from the fact that each running process must have it's
own license; my school does not have an unlimited number of such licenses,
and even if they did, I have had lots of trouble getting it to work.

The speed impacts are not anticipated to be significant; numpy benchmarks do
not typically have much difference from similar MATLAB code.
