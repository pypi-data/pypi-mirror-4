
try:
    import numpy
    from numpy.linalg import cholesky
    from numpy import transpose
    multiply = numpy.dot
except ImportError:
    import numpypy as numpy
    
    def cholesky(A):
        n = A.shape[0]
        assert A.shape == (n,n)
        L = numpy.zeros((n,n))
        
        for i in xrange(n):
            v = L[i,:i]
            L[i,i] = numpy.sqrt( A[i,i] - numpy.dot(v,v) )
            for j in xrange(i+1,n):
                L[j,i] = (A[i,j] - numpy.dot(L[i,:i],L[j,:i]))/L[i,i] 
        return L

    def transpose(A):
        n,m = A.shape
        B = numpy.empty((m,n))
        for i in xrange(n):
            B[:,i] = A[i,:]
        return B
    
    def sum1(A):
        n,m = A.shape
        result = numpy.zeros(n)
        for i in xrange(m):
            result += A[:,i]
        return result
    
    def multiply(A,b):
        return sum1(A*b)

import sys, random, bisect, multiprocessing, signal, time

def status(*items):
    """ Display a status string. """
    string = ' '.join( str(item) for item in items )
    if sys.stderr.isatty():
        sys.stderr.write('\r  \x1b[K\x1b[34m' + string + '\x1b[m\r')
        sys.stderr.flush()


#class Noiser(object):
#    def __init__(self, dim, initial):
#        self.dim = dim
#        self.covar = numpy.identity(dim) * pow(dim,-0.5)
#        self.decomp = numpy.linalg.cholesky(self.covar)
#        self.n = 2
#    
#    def record(self, value):
#        decay = 0.1 / (self.dim*self.dim)
#        
#        self.covar *= 1.0-decay
#        self.covar += decay*value[:,None]*value[None,:]
#        self.n += 1
#        
#        #Limit the complexity to O(dim^2)
#        if self.n % self.dim == 0:
#            self.decomp = numpy.linalg.cholesky(self.covar)
#    
#    def generate(self):
#        update = numpy.dot(self.decomp, numpy.random.normal(size=self.dim))
#        return update # numpy.exp(2-pow(numpy.random.random(),-0.333))


class Noiser(object):
    def __init__(self, dim, initial, rate):
        self.rate = rate
        self.dim = dim
        self.covar = numpy.identity(dim) * initial / dim
        #self.var = numpy.ones(dim) * initial / dim
        #self.decomp = cholesky(self.covar)
        self.n = 2
        self.history = [ ]
    
    def record(self, score, value, foo=True):
        decay = 1. / self.rate #(self.dim*self.dim) #* pow(self.n, -4) #* pow(self.n, -1.0/2) #/ self.dim

        ##if len(self.history) >= 256:
        ##    #if random.random()*self.rate < len(self.history):
        ##    #self.history[random.randrange(len(self.history))] = score
        ##    del self.history[0]
        ##    self.history.append(score)
        ##else:
        ##    self.history.append(score)
        ##    #del self.history[0]
        ##
        ##if not foo: return
        ##
        ##if score > min(self.history): return
        
        #p = 0
        #for item in self.history:
        #    if score > item: p += 1
        #p = float(p) / len(self.history)
        #
        #p = 1.0-16.0*p
        #if p < 0.0: return
        #decay *= p
        
        #p = 1.0-4.0*float(bisect.bisect_left(sorted(self.history), score))/len(self.history)
        #if p < 0.0: return
        #decay *= p
        
        #if score > sorted(self.history)[len(self.history) // 4]:
        #    return

        self.covar *= 1.0-decay
        #outer = numpy.empty((self.dim,self.dim))
        #for i in xrange(self.dim):
        #    outer[i,:] = value
        #for i in xrange(self.dim):
        #    outer[:,i] *= value
        outer = value[:,None]*value[None,:]
        self.covar += decay*outer

        #self.var *= 1.0-decay
        #self.var += decay*value*value

        self.n += 1

        #if self.n % self.dim == 0:
        #    self.decomp = cholesky(self.covar)
    
    def generate(self):
        v = numpy.array([ random.normalvariate(0,1) for i in range(self.dim) ])
        v /= numpy.sqrt(numpy.average(v*v))
        
        #if random.random() < 0.1:
        #    result = v / numpy.sqrt(self.var)
        #else:
        result = multiply(cholesky(self.covar), v) #* random.normalvariate(1,0.25) #/ random.normalvariate(0,1)
        
        #for i in range(self.dim):
        #    if random.random() < 0.5: 
        #        result[i] = 0
        
        return result, result # * random.normalvariate(0,1) / random.normalvariate(0,1), result


class Noisers(object):
    def __init__(self, dim, initial):
        #self.noisers = [ Noiser(dim,initial,2**i) for i in range(4,11) ]
        self.noisers = [ Noiser(dim,initial,2**i) for i in range(6,13) ]
        self.n = 0
    
    def generate(self):
        self.n += 1
        
        maxn = 1
        while maxn < len(self.noisers) and self.noisers[maxn].rate <= self.noisers[maxn].n: 
            maxn += 1
        i = random.randrange(maxn)
        #i = 0
        #while i < len(self.noisers)-1 and random.random() < 0.5:
        #    i += 1
        update, ticket = self.noisers[i].generate()
        return update, (i,ticket)
    
    def record(self, score, outer_ticket):
        (i,ticket) = outer_ticket
        #self.noisers[i].record(score, ticket)
        for j, noiser in enumerate(self.noisers):
        #for noiser in self.noisers[:i+1]:
            noiser.record(score, ticket, i==j)


def worker(scorer, fut):
    from nesoni import legion
    while True:
        value = legion.coordinator().get_future(fut)
        if value is None: break
        
        item, reply_fut = value
        result = scorer(item)        
        fut = legion.coordinator().new_future()
        legion.coordinator().deliver_future(reply_fut, (result, fut))


def improve(comment, scorer, start_x, iterations=200000, initial_accuracy=0.001, monitor = lambda x: None):
    from nesoni import legion
    
    def inflate(x, iters): return tuple( i*(1.0+0.5*((1.0-float(iters)/iterations)**2)) for i in x )  #1.2
    
    pool_size = legion.coordinator().get_cores() * 8
    
    worker_futs = [ legion.coordinator().new_future() for i in xrange(pool_size) ]
    reply_futs = [ ]
    
    for fut in worker_futs:
        legion.future(worker,scorer,fut)
    
    last_t = 0.0
    try:
        best = current = start_x
        best_score = current_score = scorer(list(current))
        
        noiser = Noisers(len(start_x), initial_accuracy)
        n_good = 0
        n_real = 0
        i = 0
        jobs = [ ]
        cutoff = inflate(current_score, 0)
        while n_real < iterations or reply_futs:
            while worker_futs and n_real < iterations :
                update, ticket = noiser.generate()            
                new = list(float(item) for item in numpy.array(best) + update)
                
                reply_fut = legion.coordinator().new_future()
                worker_fut = worker_futs.pop(0)
                
                legion.coordinator().deliver_future(worker_fut, (new, reply_fut))
                reply_futs.append( (ticket,new, reply_fut) )
                
            

            t = time.time()
            if t > last_t+20.0:
                status(comment, n_good, 'of', n_real, 'of', i, best_score, current_score, cutoff)
                if current_score[0] == 0:
                    monitor(current)
                last_t = time.time()
            
            ticket, new, reply_fut = reply_futs.pop(0)
            new_score, worker_fut = legion.coordinator().get_future(reply_fut)
            worker_futs.append(worker_fut)

            #update, ticket = noiser.generate()         
            #new = list(float(item) for item in numpy.array(best) + update)            
            #new_score = scorer2(new)
            
            cutoff = min(cutoff,inflate(new_score, n_real))
            
            if new_score[0] == 0.0:
                n_real += 1
                    
            if new_score <= cutoff:
                current_score = new_score
                current = new
                n_good += 1
                noiser.record(new_score, ticket)
            
                if new_score < best_score:
                    best_score = new_score
                    best = new
            
            #else:
            #    current_score = best_score
            #    current = best
            
            i += 1
        
        status('')
        sys.stderr.write('%s %s\n' % (comment, repr(best_score)))
        
    finally:
        #pool.terminate()
        pass
    
    while worker_futs:
        legion.coordinator().deliver_future(worker_futs.pop(0), None)
    
    return best
        