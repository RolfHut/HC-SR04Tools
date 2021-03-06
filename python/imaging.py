import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import time

###########################################################################################
# Imaging script for DEF assignment
# Authors: Eric Verschuur, Rolf Hut
# Date   : March 20, 2019
# Delft University of Technology
###########################################################################################

# To read from CSV file, in this case with ; separation - uncomment this statement
# data= pd.read_csv('DEF_metingen_test.csv', sep=",", header=None, names=["xs", "ys", "xr", "yr", "R"])

# Or direct input in the code
# make sure that each measurement is givven by 5 numbers (in cm):
# only use the VALID measurements, not the one with maximum distance that missed the object.
# Put them ins this order per line:
# Source_x Source_y Receiver_x Receiver_y Distance

data = pd.DataFrame(columns=["xs", "ys", "xr", "yr", "R"], data=[
    [0,50,0,40,41.2],
    [0,40,0,30,41.2],
    [0,30,0,20,41.2],
    [10,0,40,0,50.0],
    [20,0,50,0,50.0],
    [30,0,60,0,50.0]
    ])

# just check the data
print(data)

###########################################################################################
# DO NOT CHANGE ANYTHING BELOW THIS LINE
###########################################################################################

# assign arrays to the columns of the input
xs=data['xs']
ys=data['ys']
xr=data['xr']
yr=data['yr']
R=data['R']

# number of points in each array
n=len(R)

# plot all these points

# define midpoints for all measurements
xm=(xs+xr)/2
ym=(ys+yr)/2

# define offset for all measurements
offset=np.sqrt((xs-xr)*(xs-xr)+(ys-yr)*(ys-yr))

# define distance from midpoint to ellipse point
d=0.5*np.sqrt(R*R-offset*offset)

# define the ellipse point from midpoint
vecx=d*(ys-yr)/offset
vecy=-d*(xs-xr)/offset

# define new figure
plt.figure(figsize=(8,8))
axes = plt.gca()
axes.set_xlim([0,70])
axes.set_ylim([0,70])
plt.xlabel('X-axis (cm)')
plt.ylabel('Y-axis (cm)')

# plot the ellipses
for i in range(n):
    # plot the source and receiver location
    plt.plot(xs[i],ys[i],'ro')
    plt.plot(xr[i],yr[i],'bo')
    # plot the ellipe point from the midpoint
    if (xm[i]+vecx[i])>0:
        scl=1
    else:
        scl=-1
    # plot points away from the ellipse
    teta=np.arctan2(ys[i]-yr[i],xs[i]-xr[i])
    # define array of ellipse points
    th = np.linspace(0,2*np.pi,100);
    # calculate x and y points
    x = xm[i] + 0.5*R[i]*np.cos(th)*np.cos(teta) - d[i]*np.sin(th)*np.sin(teta);
    y = ym[i] + 0.5*R[i]*np.cos(th)*np.sin(teta) + d[i]*np.sin(th)*np.cos(teta);
    plt.plot(x,y)
    # h=ellipse(xm(i),ym(i),R(i)/2,d(i),teta)
    # print(teta)

    
# starting values of parameters and search range
x00=45
y00=45
alpha0=0.0
beta0=0.0
d_xy=30
d_angle=45

# make array for nbest values with lowest objfun
nbest=10
x0minbest=np.zeros(nbest)
y0minbest=np.zeros(nbest)
alphaminbest=np.zeros(nbest)
betaminbest=np.zeros(nbest)
objfunminbest=np.zeros(nbest)+9999
objfunmin=9999

# eps defines weight of slopes in objfun
eps=2.0

# number of random search points
nrand=5000

# number of iterations
niter=10

# iterate over new starting points
for iter in range(niter):
    # do random search around initial value
    for j in range(nrand):
        # generate random settings of the variables
        if j==0:
            x0=x00
            y0=y00
            alpha=alpha0
            beta=beta0
        else:
            fact=2*np.random.rand(4)-1.0
            x0=x00+fact[0]*d_xy
            y0=y00+fact[1]*d_xy
            alpha=alpha0+fact[2]*d_angle
            beta=beta0+fact[3]*d_angle
        # set up left branche
        dy=np.linspace(0,30,31)
        y1=y0+dy
        x1=x0+dy*np.tan(beta*np.pi/180)
        # set up right branche
        dx=np.linspace(0,30,31)
        x2=x0+dx
        y2=y0+dx*np.tan(alpha*np.pi/180)
        # calculate distance to all points
        Dmin=np.zeros(n)
        Imin=np.zeros(n)
        slope=np.zeros(n)
        for i in range(n):
            # calculate the distances
            DR1=np.sqrt(np.square(x1-xr[i])+np.square(y1-yr[i]))
            DS1=np.sqrt(np.square(x1-xs[i])+np.square(y1-ys[i]))
            DR2=np.sqrt(np.square(x2-xr[i])+np.square(y2-yr[i]))
            DS2=np.sqrt(np.square(x2-xs[i])+np.square(y2-ys[i]))
            D1=np.abs(DR1+DS1-R[i])
            D2=np.abs(DR2+DS2-R[i])
            D1D2=np.concatenate((D1,D2), axis=0)
            # find minimum and it index
            # Dmin[i],Imin[i] = min( (D1D2[i],i) for i in range(len(D1D2)) )
            Dmin[i]=min(D1D2)
            Imin[i]=np.argmin(D1D2)
            DR=np.concatenate((DR1,DR2), axis=0)
            DS=np.concatenate((DS1,DS2), axis=0)
            ii=int(min(max(1,Imin[i]),len(DR)-2))
            # determine the slope in the closest point of ellipse
            slope[i]=DR[ii+1]+DS[ii+1]-DR[ii-1]-DS[ii-1]
        # determine objective function value: sum of distance and slope errors
        D_aver=np.mean(Dmin)
        slope_aver=np.mean(abs(slope))
        objfun=D_aver+eps*slope_aver
        #
        # check if this one is better
        if objfun<objfunmin:
            print("New minimum x0=%6.3f y0=%6.3f alpha=%6.3f beta=%6.3f" % (x0,y0,alpha,beta))
            print("            D_aver=%6.3f  slope_aver=%6.3f objfun=%6.3f"% (D_aver,slope_aver,objfun))
            # plot this object
            plt.plot(x1,y1,'r',linewidth=0.5)
            plt.plot(x2,y2,'r',linewidth=0.5)
            #plt.pause(0.1)
            # save these values
            x0min=x0
            y0min=y0
            alphamin=alpha
            betamin=beta
            # save the plotted object
            x1min=x1
            y1min=y1
            x2min=x2
            y2min=y2
            objfunmin=objfun
            time.sleep(1)
        #
        # check if it is within the best values and unique
        if (objfun<objfunminbest[nbest-1]):
            # check which position
            k=0
            while objfun>objfunminbest[k]:
                k=k+1;
            # only accept is it is really different
            if objfun != objfunminbest[k-1]:
                perc=100*j/nrand
                print("Iter %2d out of %2d perc=%5.1f : better objfun value %6.3f for pos=%2d" % (iter+1,niter,perc,objfun,k))
                x0minbest[k+1:nbest-1]=x0minbest[k:nbest-2]
                x0minbest[k]=x0
                y0minbest[k+1:nbest-1]=y0minbest[k:nbest-2]
                y0minbest[k]=y0
                alphaminbest[k+1:nbest-1]=alphaminbest[k:nbest-2]
                alphaminbest[k]=alpha
                betaminbest[k+1:nbest-1]=betaminbest[k:nbest-2]
                betaminbest[k]=beta
                objfunminbest[k+1:nbest-1]=objfunminbest[k:nbest-2]
                objfunminbest[k]=objfun;
    # plot final again for this iteration
    plt.plot(x1min,y1min,'m',linewidth=2.0)
    plt.plot(x2min,y2min,'m',linewidth=2.0)
    
    # end of this iteration
    print("###############################################################################")
    print("end of iteration ",iter+1)
    # display final result for parameters with standard deviation
    print("Best alpha= %6.2f with standard deviation= %6.2f" % (np.mean(alphaminbest),np.std(alphaminbest)))
    print("Best beta = %6.2f with standard deviation= %6.2f" % (np.mean(betaminbest),np.std(betaminbest)))
    print("Best x0   = %6.2f with standard deviation= %6.2f" % (np.mean(x0minbest),np.std(x0minbest)))
    print("Best y0   = %6.2f with standard deviation= %6.2f" % (np.mean(y0minbest),np.std(y0minbest)))
    print("###############################################################################")
    time.sleep(1)
    # next iteration; take output as initial values and smaller search area
    x00=x0min
    y00=y0min
    alpha0=alphamin
    beta0=betamin
    d_xy=max(1,2*(np.std(x0minbest)+np.std(y0minbest)))
    d_angle=max(2,2*(np.std(alphaminbest)+np.std(betaminbest)))

plt.show()

# define new figure te replot ellipses and optimum object
plt.figure(figsize=(8,8))
axes = plt.gca()
axes.set_xlim([0,70])
axes.set_ylim([0,70])
plt.xlabel('X-axis (cm)')
plt.ylabel('Y-axis (cm)')

# plot the ellipses
for i in range(n):
    # plot the source and receiver location
    plt.plot(xs[i],ys[i],'ro')
    plt.plot(xr[i],yr[i],'bo')
    # plot the ellipe point from the midpoint
    if (xm[i]+vecx[i])>0:
        scl=1
    else:
        scl=-1
    # plot points away from the ellipse
    teta=np.arctan2(ys[i]-yr[i],xs[i]-xr[i])
    # define array of ellipse points
    th = np.linspace(0,2*np.pi,100);
    # calculate x and y points
    x = xm[i] + 0.5*R[i]*np.cos(th)*np.cos(teta) - d[i]*np.sin(th)*np.sin(teta);
    y = ym[i] + 0.5*R[i]*np.cos(th)*np.sin(teta) + d[i]*np.sin(th)*np.cos(teta);
    plt.plot(x,y)
    # h=ellipse(xm(i),ym(i),R(i)/2,d(i),teta)
    # print(teta)
    

# plot best object location
plt.plot(x1min,y1min,'k',linewidth=4.0)
plt.plot(x2min,y2min,'k',linewidth=4.0)
plt.show()


# For QC: figure with besy objfun values
# plt.figure()
# plt.plot(objfunminbest)
# plt.pause(0.1)

