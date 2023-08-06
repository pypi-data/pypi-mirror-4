from __future__ import division
from numpy import *
import numpy

spline_order = 2
Nvec = [30,40,50,]
values = []

for N in Nvec:

    orders = array([N,N])

    smin = array([0,0], dtype=float)
    smax = array([1,1], dtype=float)

    rvec = linspace( smin[0],smax[0],orders[0])
    cvec = linspace( smin[1],smax[1],orders[1])

    from dolo.numeric.misc import cartesian

    points = cartesian( [rvec, cvec ]).T

    oorders = array([500,500])
    ppoints = cartesian( [ linspace( smin[0],smax[0],oorders[0]), linspace( smin[1],smax[1],oorders[1])] ).T


    fun = lambda a,b: a * exp( b )

    Z = fun(points[0,:], points[1,:])
    ZZ = fun(ppoints[0,:], ppoints[1,:])

    sh = orders - 1

    Z = Z.reshape(orders)
    ZZ = ZZ.reshape(oorders)



    coordinates = (points-smin[:,None])/(smax[:,None]-smin[:,None]) * sh[:,None]
    print(coordinates)
    from scipy.ndimage import map_coordinates
    test = map_coordinates( Z, coordinates , order=spline_order)
    test = test.reshape(orders)
    print('order 1')
    print(points.shape)
    print(abs(test - Z).max())



    ssh = array( orders - 1, dtype=float )
    ccoordinates = (ppoints-smin[:,None])/((smax-smin)[:,None])* sh[:,None]
    print(ccoordinates)

    from scipy.ndimage import spline_filter
    print('c')
    Z_filtered = spline_filter(Z, spline_order, output=numpy.float64)
    print(ccoordinates)
    ttest = map_coordinates( Z_filtered, ccoordinates, order=spline_order, prefilter=True)
#    ttest = map_coordinates( Z, ccoordinates, order=spline_order, prefilter=False)

    ttest = ttest.reshape(oorders)
    print(ppoints.shape)
    print(ttest.shape)
    print(ZZ.shape)
    print( (abs(ttest - ZZ)).max())

    values.append(  (abs(ttest - ZZ)).max()  )




import matplotlib.pyplot as plt

plt.plot(Nvec, values)
plt.show()










import matplotlib.pyplot as plt
xs = ppoints[0,:].reshape(oorders)
ys = ppoints[1,:].reshape(oorders)
zs = ZZ.flatten().reshape(oorders)
zs_a = ttest.flatten().reshape(oorders)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(xs, ys, zs-zs_a)
#ax.plot_surface(xs, ys, zs)
#ax.plot_surface(xs, ys, zs_a)
ax.grid(True, linestyle='--',color='0.75')
plt.show()