import os
import numpy as np
import dclaw.fortconvert as cf
import matplotlib.pyplot as plt
"""
this routine creates time series output along a transect from fort.q files.
for time series with higher time resolution than fort output use the gauge feature prior to runtime
script is intended to be run from top-level simulation directory above _output/.
"""


#time series locations (x,y). 

#transect definition
N = 5 #number of points along transect
#two points for line segment
x0 = 0.
y0 = 0.
x1 = 4.0
y1 = 4.0

X0 = np.array([x0,y0])
X1 = np.array([x1,y1])
L = X1 - X0
D = np.sqrt(L[0]**2+L[1]**2) 
Lhat = (1.0/D)*L #unit 

dl = D/(N-1) #segment length
dL = dl*Lhat #segment vector

dx = dl*np.array(range(N))
x = []
for dxi in dx:
	xp = X0 + dxi*Lhat
	x.append(xp)

#get current directory
pwd = os.path.abspath('./')

#location of output to be read (fort.qXXXX and fort.tXXXX)
fortoutputdir = os.path.join(pwd,'_output')

#directory to store time series output files
outdirname = os.path.join(pwd,'_timeseries_transect')
if not os.path.isdir(outdirname):
	cmdstr = 'mkdir '+outdirname
	os.system(cmdstr)
else:
	if os.listdir(outdirname):
		print ('output directory is not empty')
		g = raw_input('Continue: y/n? ')
		if g[0] == 'y' or g[0] == 'Y':
			pass
		else:
			print 'exiting'
			exit()


#number of gauges (locations)
Ng = len(x) 
Ngs = range(Ng)


#create files to store time series, or read files if they exist
#for each file/location create array to be put in container list of arrays 
#files and arrays have columns t,q1,...,q8. One row for each frame number

#Note: this routine assumes that all preexisting time series files have the same number of rows/frames
Mlist = []
for ig in Ngs:
	tsfname = 'Gauge_'+str(ig)+'.txt'
	fname = os.path.join(outdirname,tsfname)
	if os.path.isfile(fname):
		M = np.loadtxt(fname)
	else:
		#create array and add first row for t=0.
		fqname = os.path.join(fortoutputdir,'fort.q0000')
		ftname = os.path.join(fortoutputdir,'fort.t0000')
		ftheader = cf.forttheaderread(ftname)
		t = ftheader['time']
		print('reading frame '+fqname)
		solutionlist = cf.fort2list(fqname,ftname)
		xig = x[ig]
		qig=cf.pointfromfort(xig,solutionlist)
		tqig = np.hstack((t,qig))
		M = np.reshape(tqig,(1,9))

	nrows = len(M)
	Mlist.append(M)
	

# frame numbers (fort.qXXX0 - fort.qXXXN) f1 - f2.
#Note: f1 based on the size of M from above. To restrict range of fort files read, modify f1 
f1 = nrows #note: begin at number of rows due to 0 index for fort.q0000
f2 = 68 #choose final frame (could count #fort. files instead)
frames = range(f1,f2+1) #which frames
frameN = range(len(frames)) #frame indices

#NOTE: this routine needs to complete to save progress of reading fort files: should probably be improved later
#loop through frames selected
for fi in frameN:
	frame = frames[fi]
	framex = str(1000 + frame)
	framename = framex[1:]
	fqname = os.path.join(fortoutputdir,'fort.q0' + framename)
	ftname = os.path.join(fortoutputdir,'fort.t0' + framename)
	print('reading frame '+fqname)
	ftheader = cf.forttheaderread(ftname)
	t = ftheader['time']
	solutionlist = cf.fort2list(fqname,ftname)

	#loop through number of points (gauges) to find in frame/solution
	for ig in Ngs:
		#location of gauge
		xig = x[ig]
		#solution at gauge
		qig=cf.pointfromfort(xig,solutionlist)
		tqig = np.hstack((t,qig))
		M = Mlist[ig]
		M=np.vstack((M,tqig))
		Mlist[ig] = M


#save the arrays to files (THIS WILL OVERWRITE THE PREVIOUS TIME SERIES FILES)	
for ig in Ngs:
	M = Mlist[ig]
	tsfname = 'Gauge_'+str(ig)+'.txt'
	fname = os.path.join(outdirname,tsfname)
	np.savetxt(fname,M)




"""









