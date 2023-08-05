#!/usr/bin/env python

from pyper import *

if __name__ == '__main__':
	# generate a R instance
	r = R()

	# disable numpy & pandas in R
	r.has_numpy = False
	r.has_pandas = False

	# run R codes
	r.run('a <- 3')
	r('a <- 3')
	r(['a <- 3', 'b <- a*2', 'print(b)'])
	r('png("abc.png"); plot(1:5); dev.off()') # plotting in R

	# test parameter conversion
	a = range(5)
	r('b <- %s' % Str4R(a))

	# set variables in R
	r.assign('b', a)
	r['b'] = a
	r.b = a

	# get value from R 
	b = r['b']
	b = r.b
	pi = r['pi']
	pi = r.pi
	# or from a more complex R expression
	val = r['(2*pi + 3:9)/5']
	# get value from R variables that may not exist
	bb = r.get('bb', 'No this variable!')

	# delete R variables
	del(r.a, r['b'])

	# test for more data structure
	print('\n\n-------Test without numpy & pandas----------\n')
	r.avec = 0, 1, 2, 3, 4
	r.alist = [1, (2, 3, 'any strings'), 4+5j]
	r('amat <- matrix(0:11, nrow=3, byrow=TRUE)')
	r('aary <- array(0:23, dim=c(3,4,2))')
	r('adfm <- data.frame(aa=1:3, bb=paste("s", 2:4, sep="-"))')
	print('R vector (avec): ' + repr(r.avec))
	print('R list (alist): ' + repr(r.alist))
	print('R matrix (amat): ' + repr(r.amat))
	print('R array (aary): ' + repr(r.aary))
	print('R data frame (adfm): ' + repr(r.adfm))

	if has_numpy:
		print('\n\n-------Test with numpy----------\n')
		r.has_numpy = True
		arange, array, reshape = numpy.arange, numpy.array, numpy.reshape
		# numpy arrays
		# one-dimenstion numpy array will be converted to R vector
		r.bvec = arange(5)
		# two-dimenstion numpy array will be converted to R matrix
		r.bmat = reshape(arange(12), (3, 4)) # a 3-row, 4-column matrix
		# numpy array of three or higher dimensions will be converted to R array
		r.bary = reshape(arange(24), (2, 3, 4)) # a 3-row, 4-column, 2-layer array 
		# one-dimenstion numpy record array will be converted to R data.framme
		r.bdfm = array([(1, 'Joe', 35820.0), (2, 'Jane', 41235.0), (3, 'Kate', 37932.0)], \
				dtype=[('id', '<i4'), ('employee', '|S4'), ('salary', '<f4')])
		print('R vector (avec): ' + repr(r['avec']))
		print('R vector (bvec): ' + repr(r['bvec']))
		print('R matrix (amat): ' + repr(r['amat']))
		print('R matrix (bamat): ' + repr(r['bmat']))
		print('R array (aary): ' + repr(r['aary']))
		print('R array (bary): ' + repr(r['bary']))
		print('R data frame (adfm): ' + repr(r['adfm']))
		print('R data frame (bdfm): ' + repr(r['bdfm']))

	if has_pandas:
		print('\n\n-------Test with pandas----------\n')
		r.has_pandas = True
		print('R data frame (adfm): ' + repr(r.adfm))
		if has_numpy:
			print('R data frame (bdfm): ' + repr(r['bdfm']))


	# test huge data sets and the function runR
	print('\n\n-------Test for huge data sets----------\n')
	a = range(10000) #00)
	sa = 'a <- ' + Str4R(a)
	rlt = runR(sa, Robj=r) # If you want to launch a new R process. use "runR(sa)" or "runR(sa, Robj='path_to_R')" instead.
	print(rlt)

	print('\nTest passed!\n\n')

	del(r) # to eliminate the possible DOS windows

	# to use an R on remote server, you need to provide correct parameter to initialize the R instance:
	# rsrv = R(RCMD='/usr/local/bin/R', host='My_server_name_or_IP', user='username')


