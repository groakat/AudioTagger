
import matplotlib.colors as col
import matplotlib.cm as cm

def register_own_cmap():
	"""
	Function that defines colormap to be used to view spectrograms.

	Register_own_cmap code from http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps.

	Colormap colours are adapted from gist_stern colormap in Matplotlib library, available: 

	https://github.com/matplotlib/matplotlib/blob/ab3aa58867ecce6cc6c377c8aaff1e6074a27cdb/lib/matplotlib/_cm.py

	"""
	cdict = {'red': ((0.000, 0.000, 0.000),
	                 (0.0547, 1.000, 1.000), 
	                 (0.250, 0.027, 0.250), 
	                 (0.900, 1.000, 1.000), 
	                 (1.000, 1.000, 1.000)),
	         'green': ((0, 0, 0), (0.900, 1.000, 1.000), (1, 1, 1)),
	         'blue': ((0.000, 0.000, 0.000), 
	         		  (0.400, 1.000, 1.000),
	                  (0.735, 0.000, 0.000), 
	                  (0.900, 1.000, 1.000), 
	                  (1.000, 1.000, 1.000))}

	Spectro_Colormap = col.LinearSegmentedColormap('spec_colormap', cdict)
	cm.register_cmap(name='specColormap',cmap=Spectro_Colormap)

if __name__ == "__main__":
    register_own_cmap()
