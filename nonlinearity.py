"""
Ted Moskovitz, 2018
Plot nonlinearity for 2-filter neural network model generated by Keras
"""

import numpy as np
import keras 
from keras.models import Sequential, load_model
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
import scipy.signal as spsig
import scipy.ndimage as spnd
fig = plt.figure()

def gram_schmidt_columns(X):
    """
    Compute Gram-Schmidt orthogonalization of X.
    
    Args: 
        X: input matrix
    
    Returns: 
        Q: concatenated orthogonalized basis vectors
    """
    Q, R = np.linalg.qr(X)
    return Q

def generate(model, bound=1.5, es=False):
    """
    Genereate the 3-D model nonlinearity. 
    
    Args: 
        model: a trained Keras model
        bound: limit of the effective domain
        
    Returns: 
        x, y: input meshes
        z: nonlinearity output z = f(x,y)
    """
    # get weights
    weights = []
    for layer in model.layers:
        weights.append(layer.get_weights())
        
    filters = weights[0][0] if not es else weights[1][0]
    if es and filters.shape[1] < 2:
        filters = np.hstack([weights[1][0].reshape(-1,1), weights[2][0].reshape(-1,1)])
    assert (filters.shape[1] == 2), "Model has incorrect number of filters ({})".format(filters.shape[1])

    rawf1 = filters[:,0].reshape(-1,1)
    rawf2 = filters[:,1].reshape(-1,1)
    F = np.hstack([rawf1,rawf2])
    np.savetxt('./Matlab_Models/simple_2f.csv', F, delimiter=',')
    F_o = gram_schmidt_columns(F)
    
    # normalize
    F_o[:,0] /= np.linalg.norm(F_o[:,0])
    F_o[:,1] /= np.linalg.norm(F_o[:,1])
    f1 = F_o[:,0]
    f2 = F_o[:,1]

    # check filter responses to calibrate grid
    xgrid = np.arange(-bound, bound, .01)
    ygrid = np.arange(-bound, bound, .01)
    npts = len(xgrid)
    x,y = np.meshgrid(xgrid, ygrid)
    z = np.zeros((npts, npts))
   
    count = 0
    for ix in range(npts):
        for iy in range(npts):
            if count % (int(npts*npts)/5) == 0 and count > 0: # track progress cause it's slow
                print (str(count) + " / " + str(npts*npts) + ' points computed')
            #f1b = np.tile(f1, [npts,1])
            #f2b = np.tile(f2, [npts,1])
            #z[ix,:] = nn(x[ix,:].reshape(npts,1)*f1b + y[ix,:].reshape(npts,1)*f2b)
            #inp = x[ix,:].reshape(npts,1)*f1b + y[ix,:].reshape(npts,1)*f2b
            inp = np.reshape(x[ix,iy]*f1 + y[ix,iy]*f2, [1,-1])
            
            z[ix,iy] = model.predict(inp)
            count += 1
        
    return x,y,z


def plot(in_, label=False, rot=260, lim=0, cmap='hot'):
    """
    Plots the nonlinearity. 
    
    Args: 
        in_: cache of x,y,z values
        label: whether to label the plot
        rot: rotation of 3D mesh (degrees)
        lim: extent of the plotting window (0 means no limit)
        
    """
    x,y,z = in_
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    if label: ax.plot_surface(x, y, z, cmap='hot', label='NN', alpha=1.0);
    else: ax.plot_surface(x, y, z, cmap=cmap, alpha=1.0);

    # rotate the axes and update
    for angle in [rot]:#range(0, 360):
        ax.view_init(30, angle)
        #ax.set_zlabel('firing rate (sp/s)')
        plt.draw()
        plt.pause(.001)

    ax.legend()
    if lim > 0: ax.set_xlim([0,lim]);
    ax.set_zlabel('firing rate (spks/s)')
    plt.show()