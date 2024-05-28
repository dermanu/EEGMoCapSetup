import multiprocessing
import os                                                               
 
# Creating the tuple of all the processes
all_processes = ('ParaVideoAcq0.py', 'ParaVideoAcq1.py', 'ParaVideoAcq2.py', 'ParaVideoAcq3.py')                                    
                                                  
# This block of code enables us to call the script from command line.                                                                                
def execute(process):                                                             
    os.system(f'python {process}')                                       
                                                                                
                                                                                
process_pool = multiprocessing.Pool(processes = 4)                                                        
process_pool.map(execute, all_processes)                                                 
