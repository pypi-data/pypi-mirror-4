"""Parallelized addition and multiplication for vector spaces.

There are separate methods to operate on vectors and vector handles.
"""

import sys  
import copy
import time as T
import numpy as N

import util
from parallel import parallel_default_instance
_parallel = parallel_default_instance
import vectors as V

   
class VectorSpace(object):
    """Responsible for performing addition and multiplication in parallel.

    Kwargs:
        ``inner_product``: Inner product function.
        
        ``max_vecs_per_node``: Max number of vecs in memory per node.
        
        ``verbosity``: 1 prints progress and warnings, 0 prints almost nothing
        
        ``print_interval``: Min interval between progress messages, seconds.

    The class implements parallelized vector addition and scalar multiplication
    and is used in high-level classes ``POD``, ``BPOD``, ``DMD``
    and ``LTIGalerkinProjection``. 

    Note: Computations are often sped up by using all available processors,
    even if this lowers ``max_vecs_per_node`` proportionally. 
    However, this depends on the computer and the nature of the functions
    supplied, and sometimes loading from file is slower with more processors.
    """
    def __init__(self, inner_product=None, 
        max_vecs_per_node=None, verbosity=1, print_interval=10):
        """Constructor."""
        self.inner_product = inner_product
        self.verbosity = verbosity 
        self.print_interval = print_interval
        self.prev_print_time = 0.
        
        if max_vecs_per_node is None:
            self.max_vecs_per_node = 10000 # different default?
            self.print_msg('Warning: max_vecs_per_node was not specified. '
                'Assuming %d vecs can be in memory per node. Decrease '
                'max_vecs_per_node if memory errors.'%self.max_vecs_per_node)
        else:
            self.max_vecs_per_node = max_vecs_per_node
        
        if self.max_vecs_per_node < \
            2 * _parallel.get_num_procs() / _parallel.get_num_nodes(): 
            self.max_vecs_per_proc = 2
            self.print_msg('Warning: max_vecs_per_node too small for given '
                'number of nodes and procs. Assuming 2 vecs can be '
                'in memory per processor. If possible, increase ' 
                'max_vecs_per_node for a speedup.')
        else:
            self.max_vecs_per_proc = self.max_vecs_per_node * \
                _parallel.get_num_nodes()/_parallel.get_num_procs()
                
    def _check_inner_product(self):
        """Check that inner_product is defined"""
        if self.inner_product is None:
            raise RuntimeError('No inner product function is defined')
        
    
    def print_msg(self, msg, output_channel=sys.stdout):
        """Print a message from rank 0 if verbosity"""
        if self.verbosity > 0 and _parallel.is_rank_zero():
            print >> output_channel, msg

    def sanity_check_in_memory(self, test_vec):
        """Check user-supplied vector object. See :py:meth:`sanity_check`.
        
        Args:
            ``test_vec``: A vector.
        """
        self.sanity_check(V.InMemoryVecHandle(test_vec))

    def sanity_check(self, test_vec_handle):
        """Check user-supplied vec handle and vec objects.
        
        Args:
            ``test_vec_handle``: A vector handle.
        
        The add and mult functions are tested for the vector object.  
        This is not a complete testing, but catches some common mistakes.
        Raises an error if a check fails.
        
        TODO: Other things which could be tested:
            ``get``/``put`` doesn't effect other vecs (memory problems)
        """
        self._check_inner_product()
        tol = 1e-10

        test_vec = test_vec_handle.get()
        vec_copy = copy.deepcopy(test_vec)
        vec_copy_mag2 = self.inner_product(vec_copy, vec_copy)
        
        factor = 2.
        vec_mult = test_vec * factor
        
        if abs(self.inner_product(vec_mult, vec_mult) -
                vec_copy_mag2 * factor**2) > tol:
            raise ValueError('Multiplication of vec/mode failed')
        
        if abs(self.inner_product(test_vec, test_vec) - 
                vec_copy_mag2) > tol:  
            raise ValueError('Original vec modified by multiplication!') 
        vec_add = test_vec + test_vec
        if abs(self.inner_product(vec_add, vec_add) - vec_copy_mag2 * 4) > tol:
            raise ValueError('Addition does not give correct result')
        
        if abs(self.inner_product(test_vec, test_vec) - vec_copy_mag2) > tol:  
            raise ValueError('Original vec modified by addition!')       
        
        vec_add_mult = test_vec * factor + test_vec
        if abs(self.inner_product(vec_add_mult, vec_add_mult) - vec_copy_mag2 *
                (factor + 1) ** 2) > tol:
            raise ValueError('Multiplication and addition of vec/mode are '+\
                'inconsistent')
        
        if abs(self.inner_product(test_vec, test_vec) - vec_copy_mag2) > tol:  
            raise ValueError('Original vec modified by combo of mult/add!') 
        
        #vecSub = 3.5*test_vec - test_vec
        #N.testing.assert_array_almost_equal(vecSub,2.5*test_vec)
        #N.testing.assert_array_almost_equal(test_vec,vec_copy)
        self.print_msg('Passed the sanity check')


    def compute_inner_product_mat(self, row_vec_handles, col_vec_handles):
        """Computes a matrix of inner products and returns it.
        
        Args:
            ``row_vec_handles``: List of row vec handles.
                For example BPOD adjoints, "Y".
          
            ``col_vec_handles``: List of column vec handles.
                For example BPOD directs, "X".
        
        Returns:
            ``IP_mat``: Array of inner products.

        The vecs are retrieved in memory-efficient
        chunks and are not all in memory at once.
        The row vecs and col vecs are assumed to be different.        
        When they are the same, use :py:meth:`compute_symmetric_inner_product` 
        for a 2x speedup.
        
        Each processor is responsible for retrieving a subset of the rows and
        columns. The processors then exchange columns via MPI so it can be 
        used to compute all IPs for the rows on each processor. This is 
        repeated until all processors are done with all of their row chunks.
        If there are 2 processors::
           
                | x o |
          rank0 | x o |
                | x o |
            -
                | o x |
          rank1 | o x |
                | o x |
        
        In the next step, rank 0 sends column 0 to rank 1 and rank 1
        sends column 1 to rank 0. The remaining IPs are filled in::
        
                | x x |
          rank0 | x x |
                | x x |
            -
                | x x |
          rank1 | x x |
                | x x |
          
        When the number of cols and rows is
        not divisible by the number of processors, the processors are assigned
        unequal numbers of tasks. However, all processors are always
        part of the passing cycle.
        
        The scaling is:
        
        - num gets / processor ~ (n_r*n_c/((max-2)*n_p*n_p)) + n_r/n_p
        - num MPI sends / processor ~ (n_p-1)*(n_r/((max-2)*n_p))*n_c/n_p
        - num inner products / processor ~ n_r*n_c/n_p
            
        where n_r is number of rows, n_c number of columns, max is
        max_vecs_per_proc = max_vecs_per_node/num_procs_per_node, and n_p is
        number of processors.
        
        If there are more rows than columns, then an internal transpose
        and un-transpose is performed to improve efficiency (since n_c only
        appears in the scaling in the quadratic term).
        """
        self._check_inner_product()
        row_vec_handles = util.make_list(row_vec_handles)
        col_vec_handles = util.make_list(col_vec_handles)
            
        num_cols = len(col_vec_handles)
        num_rows = len(row_vec_handles)

        if num_rows > num_cols:
            transpose = True
            temp = row_vec_handles
            row_vec_handles = col_vec_handles
            col_vec_handles = temp
            temp = num_rows
            num_rows = num_cols
            num_cols = temp
        else: 
            transpose = False
               
        # convenience
        rank = _parallel.get_rank()

        # num_cols_per_proc_chunk is the number of cols each proc gets at once
        num_cols_per_proc_chunk = 1
        num_rows_per_proc_chunk = self.max_vecs_per_proc - \
            num_cols_per_proc_chunk         
        
        # Determine how the retrieving and inner products will be split up.
        row_tasks = _parallel.find_assignments(range(num_rows))
        col_tasks = _parallel.find_assignments(range(num_cols))
           
        # Find max number of col tasks among all processors
        max_num_row_tasks = max([len(tasks) for tasks in row_tasks])
        max_num_col_tasks = max([len(tasks) for tasks in col_tasks])
        
        # These variables are the number of iters through loops that retrieve
        # ("get") row and column vecs.
        num_row_get_loops = \
            int(N.ceil(max_num_row_tasks*1./num_rows_per_proc_chunk))
        num_col_get_loops = \
            int(N.ceil(max_num_col_tasks*1./num_cols_per_proc_chunk))
        if num_row_get_loops > 1:
            self.print_msg('Warning: The column vecs, of which '
                    'there are %d, will be retrieved %d times each. Increase '
                    'number of nodes or max_vecs_per_node to reduce redundant '
                    '"get"s for a speedup.'%(num_cols, num_row_get_loops))
        
        
        # Estimate the time this will take and determine matrix datatype
        # (real or complex).
        row_vec = row_vec_handles[0].get()
        col_vec = col_vec_handles[0].get()
        # Burn the first, it sometimes contains slow imports
        IP_burn = self.inner_product(row_vec, col_vec)
        
        start_time = T.time()
        row_vec = row_vec_handles[0].get()
        get_time = T.time() - start_time
        
        start_time = T.time()
        IP = self.inner_product(row_vec, col_vec)
        IP_time = T.time() - start_time
        IP_type = type(IP)
        
        total_IP_time = (num_rows * num_cols * IP_time /
            _parallel.get_num_procs())
        vecs_per_proc = self.max_vecs_per_node * _parallel.get_num_nodes() / \
            _parallel.get_num_procs()
        num_gets =  (num_rows*num_cols) / ((vecs_per_proc-2) *
            _parallel.get_num_procs()**2) + num_rows/_parallel.get_num_procs()
        total_get_time = num_gets * get_time
        self.print_msg('Computing the inner product matrix will take at least '
                    '%.1f minutes' % ((total_IP_time + total_get_time) / 60.))
        del row_vec, col_vec

        
        
        
        # To find all of the inner product mat chunks, each 
        # processor has a full IP_mat with size
        # num_rows x num_cols even though each processor is not responsible for
        # filling in all of these entries. After each proc fills in what it is
        # responsible for, the other entries remain 0's. Then, an allreduce
        # is done and all the IP_mats are summed. This is simpler
        # concatenating chunks of the IPmats.
        # The efficiency is not an issue, the size of the mats
        # are small compared to the size of the vecs for large data.
        IP_mat = N.mat(N.zeros((num_rows, num_cols), dtype=IP_type))
        for row_get_index in xrange(num_row_get_loops):
            if len(row_tasks[rank]) > 0:
                start_row_index = min(row_tasks[rank][0] + 
                    row_get_index*num_rows_per_proc_chunk, 
                    row_tasks[rank][-1]+1)
                end_row_index = min(row_tasks[rank][-1]+1, 
                    start_row_index + num_rows_per_proc_chunk)
                row_vecs = [row_vec_handle.get() for row_vec_handle in 
                    row_vec_handles[start_row_index:end_row_index]]
            else:
                row_vecs = []

            for col_get_index in xrange(num_col_get_loops):
                if len(col_tasks[rank]) > 0:
                    start_col_index = min(col_tasks[rank][0] + 
                        col_get_index*num_cols_per_proc_chunk, 
                            col_tasks[rank][-1]+1)
                    end_col_index = min(col_tasks[rank][-1]+1, 
                        start_col_index + num_cols_per_proc_chunk)
                else:
                    start_col_index = 0
                    end_col_index = 0
                # Cycle the col vecs to proc with rank -> mod(rank+1,numProcs) 
                # Must do this for each processor, until data makes a circle
                col_vecs_recv = (None, None)
                col_indices = range(start_col_index, end_col_index)
                for pass_index in xrange(_parallel.get_num_procs()):
                    #if rank==0: print 'starting pass index=',pass_index
                    # If on the first pass, get the col vecs, no send/recv
                    # This is all that is called when in serial, loop iterates
                    # once.
                    if pass_index == 0:
                        col_vecs = [col_handle.get() 
                            for col_handle in col_vec_handles[start_col_index:
                            end_col_index]]
                    else:
                        # Determine with whom to communicate
                        dest = (rank + 1) % _parallel.get_num_procs()
                        source = (rank - 1)%_parallel.get_num_procs()    
                            
                        # Create unique tag based on send/recv ranks
                        send_tag = rank * \
                                (_parallel.get_num_procs() + 1) + dest
                        recv_tag = source * \
                            (_parallel.get_num_procs() + 1) + rank
                        
                        # Collect data and send/receive
                        col_vecs_send = (col_vecs, col_indices)    
                        request = _parallel.comm.isend(
                            col_vecs_send, dest=dest, tag=send_tag)
                        col_vecs_recv = _parallel.comm.recv(
                            source=source, tag=recv_tag)
                        request.Wait()
                        _parallel.barrier()
                        col_indices = col_vecs_recv[1]
                        col_vecs = col_vecs_recv[0]
                        
                    # Compute the IPs for this set of data col_indices stores
                    # the indices of the IP_mat columns to be
                    # filled in.
                    if len(row_vecs) > 0:
                        for row_index in xrange(start_row_index, end_row_index):
                            for col_vec_index, col_vec in enumerate(col_vecs):
                                IP_mat[row_index, col_indices[
                                    col_vec_index]] = self.inner_product(
                                    row_vecs[row_index - start_row_index],
                                    col_vec)
                        if (T.time() - self.prev_print_time) > self.print_interval:
                            num_completed_IPs = (N.abs(IP_mat)>0).sum()
                            percent_completed_IPs = (100. * num_completed_IPs*
                                _parallel.get_num_MPI_workers()) / (
                                num_cols*num_rows)
                            self.print_msg(('Completed %.1f%% of inner ' + 
                                'products')%percent_completed_IPs, sys.stderr)
                            self.prev_print_time = T.time()
                        
                        
                # Clear the retrieved column vecs after done this pass cycle
                del col_vecs
            # Completed a chunk of rows and all columns on all processors.
            del row_vecs

        # Assign these chunks into IP_mat.
        if _parallel.is_distributed():
            IP_mat = _parallel.custom_comm.allreduce(IP_mat)

        if transpose:
            IP_mat = IP_mat.T
        
        percent_completed_IPs = 100.
        self.print_msg(('Completed %.1f%% of inner ' + 
            'products')%percent_completed_IPs, sys.stderr)
        self.prev_print_time = T.time()

        _parallel.barrier() # ensure that all procs leave function at same time
        return IP_mat


    def compute_inner_product_mat_in_memory(self, row_vecs, col_vecs):
        """Computes a matrix of inner products and returns it.
        
        Args:
            ``row_vecs``: List of row vecs.
                For example BPOD adjoints, "Y".
          
            ``col_vecs``: List of column vecs.
                For example BPOD directs, "X".
        
        Returns:
            ``IP_mat``: Array of inner products.
        
        See :py:meth:`compute_inner_product_mat`.
        """
        self._check_inner_product()
        row_vecs = util.make_list(row_vecs)
        col_vecs = util.make_list(col_vecs)
        row_vec_handles = [V.InMemoryVecHandle(v) for v in row_vecs]
        col_vec_handles = [V.InMemoryVecHandle(v) for v in col_vecs]
        return self.compute_inner_product_mat(row_vec_handles, col_vec_handles)
        
        
        
        
    def compute_symmetric_inner_product_mat(self, vec_handles):
        """Computes an upper-triangular symmetric matrix of inner products.
        
        Args:
            ``vec_handles``: List of vector handles.
        
        Returns:
            ``IP_mat``: Numpy array of inner products.

        See the documentation for :py:meth:`compute_inner_product_mat` for an
        idea how this works.
        
        TODO: JON, write detailed documentation similar to 
        :py:meth:`compute_inner_product_mat`.
        """
        self._check_inner_product()
        vec_handles = util.make_list(vec_handles)
 
        num_vecs = len(vec_handles)        
        
        # num_cols_per_chunk is the number of cols each proc gets at once.
        # Columns are retrieved if the matrix must be broken up into sets of
        # chunks.  Then symmetric upper triangular portions will be computed,
        # followed by a rectangular piece that uses columns not already in
        # memory.
        num_cols_per_proc_chunk = 1
        num_rows_per_proc_chunk = self.max_vecs_per_proc -\
            num_cols_per_proc_chunk
 
        # <nprocs> chunks are computed simulaneously, making up a set.
        num_cols_per_chunk = num_cols_per_proc_chunk * _parallel.get_num_procs()
        num_rows_per_chunk = num_rows_per_proc_chunk * _parallel.get_num_procs()

        # <num_row_chunks> is the number of sets that must be computed.
        num_row_chunks = int(N.ceil(num_vecs * 1. / num_rows_per_chunk)) 
        if num_row_chunks > 1:
            self.print_msg('Warning: The vecs, of which '
                'there are %d, will be retrieved %d times each. Increase '
                'number of nodes or max_vecs_per_node to reduce redundant '
                '"get"s for a speedup.'%(num_vecs,num_row_chunks))
    
        
        
        # Estimate the time this will take and determine matrix datatype
        # (real or complex).
        test_vec = vec_handles[0].get()
        # Burn the first, it sometimes contains slow imports
        IP_burn = self.inner_product(test_vec, test_vec)
        
        start_time = T.time()
        test_vec = vec_handles[0].get()
        get_time = T.time() - start_time
        
        start_time = T.time()
        IP = self.inner_product(test_vec, test_vec)
        IP_time = T.time() - start_time
        IP_type = type(IP)
        
        total_IP_time = (num_vecs**2 * IP_time / 2. /
            _parallel.get_num_procs())
        vecs_per_proc = self.max_vecs_per_node * _parallel.get_num_nodes() / \
            _parallel.get_num_procs()
        num_gets =  (num_vecs**2 /2.) / ((vecs_per_proc-2) *
            _parallel.get_num_procs()**2) + num_vecs/_parallel.get_num_procs()/2.
        total_get_time = num_gets * get_time
        self.print_msg('Computing the inner product matrix will take at least '
                    '%.1f minutes' % ((total_IP_time + total_get_time) / 60.))
        del test_vec

        
        # Use the same trick as in compute_IP_mat, having each proc
        # fill in elements of a num_rows x num_rows sized matrix, rather than
        # assembling small chunks. This is done for the triangular portions. 
        # For the rectangular portions, the inner product mat is filled 
        # in directly.
        IP_mat = N.mat(N.zeros((num_vecs, num_vecs), dtype=IP_type))
        for start_row_index in xrange(0, num_vecs, num_rows_per_chunk):
            end_row_index = min(num_vecs, start_row_index + num_rows_per_chunk)
            proc_row_tasks_all = _parallel.find_assignments(range(
                start_row_index, end_row_index))
            num_active_procs = len([task for task in \
                proc_row_tasks_all if task != []])
            proc_row_tasks = proc_row_tasks_all[_parallel.get_rank()]
            if len(proc_row_tasks)!=0:
                row_vecs = [vec_handle.get() for vec_handle in vec_handles[
                    proc_row_tasks[0]:proc_row_tasks[-1] + 1]]
            else:
                row_vecs = []
            
            # Triangular chunks
            if len(proc_row_tasks) > 0:
                # Test that indices are consecutive
                if proc_row_tasks[0:] != range(proc_row_tasks[0], 
                    proc_row_tasks[-1] + 1):
                    raise ValueError('Indices are not consecutive.')
                
                # Per-processor triangles (using only vecs in memory)
                for row_index in xrange(proc_row_tasks[0], 
                    proc_row_tasks[-1] + 1):
                    # Diagonal term
                    IP_mat[row_index, row_index] = self.\
                        inner_product(row_vecs[row_index - proc_row_tasks[
                        0]], row_vecs[row_index - proc_row_tasks[0]])
                        
                    # Off-diagonal terms
                    for col_index in xrange(row_index + 1, proc_row_tasks[
                        -1] + 1):
                        IP_mat[row_index, col_index] = self.\
                            inner_product(row_vecs[row_index -\
                            proc_row_tasks[0]], row_vecs[col_index -\
                            proc_row_tasks[0]])
               
            # Number of square chunks to fill in is n * (n-1) / 2.  At each
            # iteration we fill in n of them, so we need (n-1) / 2 
            # iterations (round up).  
            for set_index in xrange(int(N.ceil((num_active_procs - 1.) / 2))):
                # The current proc is "sender"
                my_rank = _parallel.get_rank()
                my_row_indices = proc_row_tasks
                my_num_rows = len(my_row_indices)
                                       
                # The proc to send to is "destination"                         
                dest_rank = (my_rank + set_index + 1) % num_active_procs
                # This is unused?
                #dest_row_indices = proc_row_tasks_all[dest_rank]
                
                # The proc that data is received from is the "source"
                source_rank = (my_rank - set_index - 1) % num_active_procs
                
                # Find the maximum number of sends/recv to be done by any proc
                max_num_to_send = int(N.ceil(1. * max([len(tasks) for \
                    tasks in proc_row_tasks_all]) /\
                    num_cols_per_proc_chunk))
                """
                # Pad tasks with nan so that everyone has the same
                # number of things to send.  Same for list of vecs with None.
                # The empty lists will not do anything when enumerated, so no 
                # inner products will be taken.  nan is inserted into the 
                # indices because then min/max of the indices can be taken.
                
                if my_num_rows != len(row_vecs):
                    raise ValueError('Number of rows assigned does not ' +\
                        'match number of vecs in memory.')
                if my_num_rows > 0 and my_num_rows < max_num_to_send:
                    my_row_indices += [N.nan] * (max_num_to_send - my_num_rows) 
                    row_vecs += [[]] * (max_num_to_send - my_num_rows)
                """
                for send_index in xrange(max_num_to_send):
                    # Only processors responsible for rows communicate
                    if my_num_rows > 0:  
                        # Send row vecs, in groups of num_cols_per_proc_chunk
                        # These become columns in the ensuing computation
                        start_col_index = send_index * num_cols_per_proc_chunk
                        end_col_index = min(start_col_index + 
                            num_cols_per_proc_chunk, my_num_rows)   
                        col_vecs_send = (
                            row_vecs[start_col_index:end_col_index], 
                            my_row_indices[start_col_index:end_col_index])
                        
                        # Create unique tags based on ranks
                        send_tag = my_rank * (
                            _parallel.get_num_procs() + 1) + dest_rank
                        recv_tag = source_rank * (
                            _parallel.get_num_procs() + 1) + my_rank
                        
                        # Send and receieve data.  The Wait() command after the
                        # receive prevents a race condition not fixed by sync().
                        # The Wait() is very important for the non-
                        # blocking send (though we are unsure why).
                        request = _parallel.comm.isend(col_vecs_send, 
                            dest=dest_rank, tag=send_tag)                        
                        col_vecs_recv = _parallel.comm.recv(source = 
                            source_rank, tag=recv_tag)
                        request.Wait()
                        col_vecs = col_vecs_recv[0]
                        my_col_indices = col_vecs_recv[1]
                        
                        for row_index in xrange(my_row_indices[0], 
                            my_row_indices[-1] + 1):
                            for col_vec_index, col_vec in enumerate(col_vecs):
                                IP_mat[row_index, my_col_indices[
                                    col_vec_index]] = self.inner_product(
                                    row_vecs[row_index - my_row_indices[0]],
                                    col_vec)
                            if (T.time() - self.prev_print_time) > self.print_interval:
                                num_completed_IPs = (N.abs(IP_mat)>0).sum()
                                percent_completed_IPs = (100.*2*num_completed_IPs *
                                    _parallel.get_num_MPI_workers())/(num_vecs**2)
                                self.print_msg(('Completed %.1f%% of inner ' + 
                                    'products')%percent_completed_IPs, sys.stderr)
                                self.prev_print_time = T.time()
                    # Sync after send/receive   
                    _parallel.barrier()  
                
            
            # Fill in the rectangular portion next to each triangle (if nec.).
            # Start at index after last row, continue to last column. This part
            # of the code is the same as in compute_IP_mat, as of 
            # revision 141.  
            for start_col_index in xrange(end_row_index, num_vecs, 
                num_cols_per_chunk):
                end_col_index = min(start_col_index + num_cols_per_chunk, 
                    num_vecs)
                proc_col_tasks = _parallel.find_assignments(range(
                    start_col_index, end_col_index))[_parallel.get_rank()]
                        
                # Pass the col vecs to proc with rank -> mod(rank+1,numProcs) 
                # Must do this for each processor, until data makes a circle
                col_vecs_recv = (None, None)
                if len(proc_col_tasks) > 0:
                    col_indices = range(proc_col_tasks[0], 
                        proc_col_tasks[-1]+1)
                else:
                    col_indices = []
                    
                for num_passes in xrange(_parallel.get_num_procs()):
                    # If on the first pass, get the col vecs, no send/recv
                    # This is all that is called when in serial, loop iterates
                    # once.
                    if num_passes == 0:
                        if len(col_indices) > 0:
                            col_vecs = [col_handle.get() \
                                for col_handle in vec_handles[col_indices[0]:\
                                    col_indices[-1] + 1]]
                        else:
                            col_vecs = []
                    else: 
                        # Determine whom to communicate with
                        dest = (_parallel.get_rank() + 1) % _parallel.\
                            get_num_procs()
                        source = (_parallel.get_rank() - 1) % _parallel.\
                            get_num_procs()    
                            
                        #Create unique tag based on ranks
                        send_tag = _parallel.get_rank() * (_parallel.\
                            get_num_procs() + 1) + dest
                        recv_tag = source*(_parallel.get_num_procs() + 1) +\
                            _parallel.get_rank()    
                        
                        # Collect data and send/receive
                        col_vecs_send = (col_vecs, col_indices)     
                        request = _parallel.comm.isend(col_vecs_send, dest=\
                            dest, tag=send_tag)
                        col_vecs_recv = _parallel.comm.recv(source=source, 
                            tag=recv_tag)
                        request.Wait()
                        _parallel.barrier()
                        col_indices = col_vecs_recv[1]
                        col_vecs = col_vecs_recv[0]
                        
                    # Compute the IPs for this set of data col_indices stores
                    # the indices of the IP_mat columns to be
                    # filled in.
                    if len(proc_row_tasks) > 0:
                        for row_index in xrange(proc_row_tasks[0],
                            proc_row_tasks[-1]+1):
                            for col_vec_index, col_vec in enumerate(col_vecs):
                                IP_mat[row_index, col_indices[
                                    col_vec_index]] = self.inner_product(
                                    row_vecs[row_index - proc_row_tasks[0]],
                                    col_vec)
                        if (T.time() - self.prev_print_time) > self.print_interval:
                            num_completed_IPs = (N.abs(IP_mat)>0).sum()
                            percent_completed_IPs = (100.*2*num_completed_IPs *
                                _parallel.get_num_MPI_workers())/(num_vecs**2)
                            self.print_msg(('Completed %.1f%% of inner ' + 
                                'products')%percent_completed_IPs, sys.stderr)
                            self.prev_print_time = T.time()
            # Completed a chunk of rows and all columns on all processors.
            # Finished row_vecs loop, delete memory used
            del row_vecs                     
        
        # Assign the triangular portion chunks into IP_mat.
        if _parallel.is_distributed():
            IP_mat = _parallel.custom_comm.allreduce(IP_mat)
       
        # Create a mask for the repeated values.  Select values that are zero
        # in the upper triangular portion (not computed there) but nonzero in
        # the lower triangular portion (computed there).  For the case where
        # the inner product is not perfectly symmetric, this will select the
        # computation done in the upper triangular portion.
        mask = N.multiply(IP_mat == 0, IP_mat.T != 0)
        
        # Collect values below diagonal
        IP_mat += N.multiply(N.triu(IP_mat.T, 1), mask)
        
        # Symmetrize matrix
        IP_mat = N.triu(IP_mat) + N.triu(IP_mat, 1).T
        
        percent_completed_IPs = 100.
        self.print_msg(('Completed %.1f%% of inner ' + 
            'products')%percent_completed_IPs, sys.stderr)
        self.prev_print_time = T.time()
        
        _parallel.barrier() # ensure that all procs leave function at same time
        return IP_mat
        
        
    def compute_symmetric_inner_product_mat_in_memory(self, vecs):
        """Computes an upper-triangular symmetric matrix of inner products.
        
        Args:
            ``vecs``: List of vectors.
        
        Returns:
            ``IP_mat``: Numpy array of inner products.
        
        See :py:meth:`compute_symmetric_inner_product_mat`.
        """
        self._check_inner_product()
        vecs = util.make_list(vecs)
        return self.compute_symmetric_inner_product_mat(
            [V.InMemoryVecHandle(v) for v in vecs])
        
        
    def compute_modes(self, mode_nums, mode_handles, vec_handles, vec_coeff_mat,
        index_from=0):
        """Compute modes from vector handles.
        
        Args:
          ``mode_nums``: List of mode numbers to compute. 
              Examples are: ``range(10)`` or ``[3, 1, 6, 8]``. 
              The mode numbers need not be sorted. 
              
          ``mode_handles``: List of handles for modes.
          
          ``vec_handles``: List of handles for vectors.
          
          ``vec_coeff_mat``: Matrix of coefficients for constructing modes. 
              [mode0 mode1 ...] = [vec0 vec1 ...] * vec_coeff_mat
              The row corresponds to the vec, the column to the mode.
              The kth column corresponds to the ``index_from + k`` mode number. 
              
        Kwargs:
          ``index_from``: Integer from which to index modes, 0, 1, or other.
        
        This method casts computing modes as a linear combination of elements.
        It rearranges the coeff matrix so that the first column corresponds to
        the first mode number in mode_nums.
        Calls ``lin_combine`` with ``sum_vecs`` as the modes and the
        ``basis_vecs`` as the vecs.
        """                   
        mode_nums = util.make_list(mode_nums)
        mode_handles = util.make_list(mode_handles)
                
        num_modes = len(mode_nums)
        num_vecs = len(vec_handles)
        
        if num_modes > num_vecs:
            raise ValueError(('Cannot compute more modes (%d) than number of '
                'vecs(%d)')%(num_modes, num_vecs))
        
        if num_modes > len(mode_handles):
            raise ValueError('More mode numbers than mode destinations')
        elif num_modes < len(mode_handles):
            print ('Warning: Fewer mode numbers (%d) than mode ' 
                'destinations(%d),'
                ' some mode destinations will not be used')%(
                    num_modes, len(mode_handles))
            mode_handles = mode_handles[:num_modes] # deepcopy?
        
        for mode_num in mode_nums:
            if mode_num < index_from:
                raise ValueError('Cannot compute if mode number is less than '
                    'index_from')
            elif mode_num-index_from > vec_coeff_mat.shape[1]:
                raise ValueError('Mode index, %d, is greater '
                    'than number of columns in the build coefficient '
                    'matrix, %d'%(mode_num-index_from,vec_coeff_mat.shape[1]))
        
        # Construct vec_coeff_mat and outputPaths for lin_combine_vecs
        mode_nums_from_zero = [mode_num-index_from for mode_num in mode_nums]
        vec_coeff_mat_reordered = vec_coeff_mat[:, mode_nums_from_zero]
        
        self.lin_combine(mode_handles, vec_handles, vec_coeff_mat_reordered)
        _parallel.barrier() # ensure that all procs leave function at same time
    
    
    def compute_modes_in_memory(self, mode_nums, vecs, vec_coeff_mat, 
        index_from=0):
        """Compute modes from vectors. 
        
        Args:
            ``mode_nums``: List of mode numbers to compute. 
                Examples are: ``range(10)`` or ``[3, 1, 6, 8]``. 
                The mode numbers need not be sorted. 
              
            ``vec_handles``: List of vectors.
          
            ``vec_coeff_mat``: Matrix of coefficients for constructing modes. 
                [mode0 mode1 ...] = [vec0 vec1 ...] * vec_coeff_mat
                The row corresponds to the vec, the column to the mode.
                The kth column corresponds to the ``index_from + k`` mode number. 
              
        Kwargs:
            ``index_from``: Integer from which to index modes, 0, 1, or other.

        Returns:
            ``modes``: List of modes.

        See :py:meth:`compute_modes`.      
        In parallel, each MPI worker returns the full list of modes.
        """
        vecs = util.make_list(vecs)
        mode_handles = [V.InMemoryVecHandle() for i in mode_nums]
        vec_handles = [V.InMemoryVecHandle(vec=vec) for vec in vecs]
        self.compute_modes(mode_nums, mode_handles, 
            vec_handles, vec_coeff_mat, index_from)
        #print 'mode handles',mode_handles
        modes = [mode_handle.get() for mode_handle in mode_handles]
        #print 'rank: %d, modes'%_parallel.get_rank(),modes
        if _parallel.is_distributed():
            for i in range(modes.count(None)):
                modes.remove(None)
            modes_list = _parallel.comm.allgather(modes)
            # all_modes is a 1D list of all processors' modes.
            all_modes = util.flatten_list(modes_list)
        else:
            all_modes = modes
        return all_modes
    
    
    def lin_combine(self, sum_vec_handles, basis_vec_handles, vec_coeff_mat):
        """Linearly combines the basis vecs and calls ``put`` on result.
        
        Args:
            ``sum_vec_handles``: List of handles for the sum vectors.
                
            ``basis_vec_handles``: List of handles for the basis vecs.
                
            ``vec_coeff_mat``: Matrix with rows corresponding to a basis vecs
                and columns to sum (lin. comb.) vecs.
                The rows and columns correspond, by index,
                to the lists basis_vec_handles and sum_vec_handles.
                ``sums = basis * vec_coeff_mat``

        Each processor retrieves a subset of the basis vecs to compute as many
        outputs as a processor can have in memory at once. Each processor
        computes the "layers" from the basis it is resonsible for, and for
        as many modes as it can fit in memory. The layers from all procs are
        summed together to form the sum_vecs and ``put`` ed.
        
        Scaling is:
        
          num gets/worker = n_s/(n_p*(max-2)) * n_b/n_p
          
          passes/worker = (n_p-1) * n_s/(n_p*(max-2)) * (n_b/n_p)
          
          scalar multiplies/worker = n_s*n_b/n_p
          
        Where n_s is number of sum vecs, n_b is number of basis vecs,
        n_p is number of processors, max = max_vecs_per_node.
        """
        sum_vec_handles = util.make_list(sum_vec_handles)
        basis_vec_handles = util.make_list(basis_vec_handles)
        num_bases = len(basis_vec_handles)
        num_sums = len(sum_vec_handles)
        if num_bases > vec_coeff_mat.shape[0]:
            raise ValueError(('Coeff mat has fewer rows %d than num of basis '
                'handles %d'%(vec_coeff_mat.shape[0],num_bases)))
                
        if num_sums > vec_coeff_mat.shape[1]:
            raise ValueError(('Coeff matrix has fewer cols %d than num of '
                'output handles %d')%(vec_coeff_mat.shape[1],num_sums))
                               
        if num_bases < vec_coeff_mat.shape[0]:
            self.print_msg('Warning: fewer bases than cols in the coeff matrix'
                ', some rows of coeff matrix will not be used')
        if num_sums < vec_coeff_mat.shape[1]:
            self.print_msg('Warning: fewer outputs than rows in the coeff '
                'matrix, some cols of coeff matrix will not be used')
        
        # Estimate time it will take
        # Burn the first one for slow imports
        test_vec_burn = basis_vec_handles[0].get()
        test_vec_burn_3 = test_vec_burn + 2.*test_vec_burn
        del test_vec_burn, test_vec_burn_3
        start_time = T.time()
        test_vec = basis_vec_handles[0].get()
        get_time = T.time() - start_time
        start_time = T.time()
        test_vec_3 = test_vec + test_vec*2.0
        add_scale_time = T.time() - start_time
        del test_vec, test_vec_3
        
        vecs_per_worker = self.max_vecs_per_node * _parallel.get_num_nodes() / \
            _parallel.get_num_MPI_workers()
        num_gets = num_sums/(_parallel.get_num_MPI_workers()*(vecs_per_worker-2)) + \
            num_bases/_parallel.get_num_MPI_workers()
        num_add_scales = num_sums*num_bases/_parallel.get_num_MPI_workers()
        self.print_msg('Linear combinations will take at least %.1f minutes'%
            (num_gets*get_time/60. + num_add_scales*add_scale_time/60.))

        
        # convenience
        rank = _parallel.get_rank()

        # num_bases_per_proc_chunk is the num of bases each proc gets at once.
        num_bases_per_proc_chunk = 1
        num_sums_per_proc_chunk = self.max_vecs_per_proc - \
            num_bases_per_proc_chunk
        
        basis_tasks = _parallel.find_assignments(range(num_bases))
        sum_tasks = _parallel.find_assignments(range(num_sums))

        # Find max number tasks among all processors
        max_num_basis_tasks = max([len(tasks) for tasks in basis_tasks])
        max_num_sum_tasks = max([len(tasks) for tasks in sum_tasks])
        
        # These variables are the number of iters through loops that retrieve 
        # ("get")
        # and "put" basis and sum vecs.
        num_basis_get_iters = int(N.ceil(
            max_num_basis_tasks*1./num_bases_per_proc_chunk))
        num_sum_put_iters = int(N.ceil(
            max_num_sum_tasks*1./num_sums_per_proc_chunk))
        if num_sum_put_iters > 1:
            self.print_msg('Warning: The basis vecs, ' 
                'of which there are %d, will be retrieved %d times each. '
                'If possible, increase number of nodes or '
                'max_vecs_per_node to reduce redundant retrieves and get a '
                'big speedup.'%(num_bases, num_sum_put_iters))
               
        for sum_put_index in xrange(num_sum_put_iters):
            if len(sum_tasks[rank]) > 0:
                start_sum_index = min(sum_tasks[rank][0] + 
                    sum_put_index*num_sums_per_proc_chunk, 
                    sum_tasks[rank][-1]+1)
                end_sum_index = min(start_sum_index+num_sums_per_proc_chunk,
                    sum_tasks[rank][-1]+1)
                # Create empty list on each processor
                sum_layers = [None]*(end_sum_index - start_sum_index)
            else:
                start_sum_index = 0
                end_sum_index = 0
                sum_layers = []

            for basis_get_index in xrange(num_basis_get_iters):
                if len(basis_tasks[rank]) > 0:    
                    start_basis_index = min(basis_tasks[rank][0] + 
                        basis_get_index*num_bases_per_proc_chunk, 
                        basis_tasks[rank][-1]+1)
                    end_basis_index = min(start_basis_index + 
                        num_bases_per_proc_chunk, basis_tasks[rank][-1]+1)
                    basis_indices = range(start_basis_index, end_basis_index)
                else:
                    basis_indices = []
                
                # Pass the basis vecs to proc with rank -> mod(rank+1,numProcs) 
                # Must do this for each processor, until data makes a circle
                basis_vecs_recv = (None, None)

                for pass_index in xrange(_parallel.get_num_procs()):
                    # If on the first pass, retrieve the basis vecs, 
                    # no send/recv.
                    # This is all that is called when in serial, 
                    # loop iterates once.
                    if pass_index == 0:
                        if len(basis_indices) > 0:
                            basis_vecs = [basis_handle.get() \
                                for basis_handle in basis_vec_handles[
                                    basis_indices[0]:basis_indices[-1]+1]]
                        else:
                            basis_vecs = []
                    else:
                        # Figure out with whom to communicate
                        source = (_parallel.get_rank()-1) % \
                            _parallel.get_num_procs()
                        dest = (_parallel.get_rank()+1) % \
                            _parallel.get_num_procs()
                        
                        #Create unique tags based on ranks
                        send_tag = _parallel.get_rank() * \
                            (_parallel.get_num_procs()+1) + dest
                        recv_tag = source*(_parallel.get_num_procs()+1) + \
                            _parallel.get_rank()
                        
                        # Send/receive data
                        basis_vecs_send = (basis_vecs, basis_indices)
                        request = _parallel.comm.isend(basis_vecs_send,  
                            dest=dest, tag=send_tag)                       
                        basis_vecs_recv = _parallel.comm.recv(
                            source=source, tag=recv_tag)
                        request.Wait()
                        _parallel.barrier()
                        basis_indices = basis_vecs_recv[1]
                        basis_vecs = basis_vecs_recv[0]
                    
                    # Compute the scalar multiplications for this set of data.
                    # basis_indices stores the indices of the vec_coeff_mat to
                    # use.
                    for sum_index in xrange(start_sum_index, end_sum_index):
                        for basis_index, basis_vec in enumerate(basis_vecs):
                            sum_layer = basis_vec * \
                                vec_coeff_mat[basis_indices[basis_index],\
                                sum_index]
                            if sum_layers[sum_index-start_sum_index] is None:
                                sum_layers[sum_index-start_sum_index] = \
                                    sum_layer
                            else:
                                sum_layers[sum_index-start_sum_index] += \
                                    sum_layer
                        if (T.time() - self.prev_print_time) > self.print_interval:    
                            self.print_msg(
                                'Completed %.1f%% of linear combinations' %
                                (sum_index*100./len(sum_tasks[rank])))
                            self.prev_print_time = T.time()
                        

            # Completed this set of sum vecs, puts them to memory or file
            for sum_index in xrange(start_sum_index, end_sum_index):
                sum_vec_handles[sum_index].put(
                    sum_layers[sum_index-start_sum_index])
            del sum_layers
        
        self.print_msg('Completed %.1f%% of linear combinations' % 100.)
        self.prev_print_time = T.time()
        # ensure that all workers leave function at same time
        _parallel.barrier() 
        
    
    def lin_combine_in_memory(self, basis_vecs, vec_coeff_mat):
        """Linearly combines the basis vecs and returns resulting vecs.
        
        Args:
            ``sum_vecs``: List of sum vectors.
                
            ``basis_vecs``: List of basis vecs.
                
            ``vec_coeff_mat``: Matrix with rows corresponding to a basis vecs
                and columns to sum (lin. comb.) vecs.
                The rows and columns correspond, by index,
                to the lists basis_vec_handles and sum_vec_handles.
                ``sums = basis * vec_coeff_mat``
        
        Returns:
            List of linearly combined vectors.
        
        See :py:meth:`lin_combine`.
        """
        basis_vecs = util.make_list(basis_vecs)
        basis_vec_handles = [V.InMemoryVecHandle(vec=v) for v in basis_vecs]
        sum_vec_handles = [V.InMemoryVecHandle() 
            for i in range(vec_coeff_mat.shape[1])]
        self.lin_combine(sum_vec_handles, basis_vec_handles, vec_coeff_mat)
        sum_vecs = [sum_vec_handle.get() for sum_vec_handle in sum_vec_handles]
        if _parallel.is_distributed():
            sum_vecs_list = _parallel.comm.allgather(sum_vecs)
            # all_sum_ves is a 1D list of all processors' sum_vecs.
            all_sum_vecs = util.flatten_list(sum_vecs_list)
            for i in range(all_sum_vecs.count(None)):
                all_sum_vecs.remove(None)
        else:
            all_sum_vecs = sum_vecs
        return all_sum_vecs

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.inner_product == other.inner_product and 
            self.verbosity == other.verbosity)
        
    def __ne__(self, other):
        return not self.__eq__(other)


