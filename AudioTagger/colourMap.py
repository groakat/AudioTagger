
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap

def getColourMap():
	"""
	Function that defines colormap to be used to view spectrograms.

	getColourMap code from http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps.

	Colormap colours are adapted from gist_stern colormap in Matplotlib library, available: 

	https://github.com/matplotlib/matplotlib/blob/ab3aa58867ecce6cc6c377c8aaff1e6074a27cdb/lib/matplotlib/_cm.py

	"""
	cdict = {'red': ((0.000, 0.000, 0.000),
			         (0.0547, 1.000, 1.000), 
			         (0.250, 0.027, 0.250), 
			         (0.900, 1.000, 1.000),
			         (0.950, 1.000, 1.000),
			         (1.000, 0.000, 0.000)),
			 'green': ((0, 0, 0), (0.900, 1.000, 1.000), (1, 0, 0)),
			 'blue': ((0.000, 0.000, 0.000), 
			          (0.400, 1.000, 1.000),
			          (0.500, 1.000, 1.000),
			          (0.600, 1.000, 1.000),
			          (0.700, 1.000, 1.000),
			          (0.735, 0.500, 0.500), 
			          (0.900, 1.000, 1.000), 
			          (1.000, 0.000, 0.000))}

	cmap1 = col.LinearSegmentedColormap('SpecCM', cdict, N=256, gamma=0.75)
	cm.register_cmap(name='specColormap',cmap=cmap1)
	return cmap1

if __name__ == "__main__":
    getColourMap()
