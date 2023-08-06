#!/usr/bin/env python
from weakref import WeakValueDictionary

class ProcessManager:
    def __init__(self):
        self.processes = WeakValueDictionary()
        self.pid = 0
        self._next_pid = self.pid + 1
    
    def new_pid(self):
        pid = self._next_pid
        self._next_pid += 1
        
        return pid
    
    def register(self, obj):
        pid = self.new_pid()
        obj._archangel_pid = pid
        obj._archangel_manager = self
        self.processes[pid] = obj

        return obj
    
    def deregister(self, pid):
        del self.processes[pid]

    def shutdown(self):
        for process in self.processes.values():
            kill(process)

class Process:
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._at_exit = []
        # add a handler to signal the Process manager that we have exited
        obj.at_exit(lambda proc: proc._archangel_manager.deregister(proc._archangel_pid))
        
        return obj
        
    def _kill(self):
        try:
            self.kill()
        except:
            # ensure that we exit corectly even if an exception is raised
            self.exit()
            raise
        else:
            self.exit()
        
    def kill(self):
        """Function hook for implementations to catch a 'kill' signal and do some 
        cleanup work
        """
        pass
        
    def at_exit(self, func, **kwargs):
        """Register a function to be called when this process exits
        
        each function registered will be called with the process instance as the
        first argument
        """
        self._at_exit.append((func, kwargs))
        
    def exit(self):
        """Notify the ProcessManager that we are done or will finish up shortly"""
        for func, kwargs in self._at_exit:
            try:
                func(self, **kwargs)
            except Exception as err:
                # TODO: log this as an exception
                pass
            
def kill(proc):
    """Send the exit signal to a process"""
    proc._kill()
