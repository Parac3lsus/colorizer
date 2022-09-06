import wget
#Run this script to download the models

url = 'http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel'
wget.download(url, out='./Models/colorization_release_v2.caffemodel')
url = 'http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2_norebal.caffemodel'
wget.download(url, out='./Models/colorization_release_v2_norebal.caffemodel')
