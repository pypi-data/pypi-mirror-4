"""A thread safe Singleton class decorator"""

try:
	import threading as _threading
except ImportError:
	import dummy_threading as _threading

class SingletonFactory(object):
	""" Takes a class and produces a singleton."""

	def __init__(self,  cls,  lock):
		""" Create a new SingletonFactory.
		Keyword arguments:
		cls -- class to produce singleton from
		lock -- Lock object shared between threads to synchronize instance access
		"""
		self._lock = lock
		self._old_cls = cls
		self._instance = None

	def new_uninstantiated(self,  cls,  *args,  **kwargs):
		""" Called when a new singleton instance is created.
		This first locks access for other threads. Then a new instance of cls is created
		and further calls to __new__ are replaced by new_instantiated
		Keyword arguments:
		cls -- instantiated class
		args, kwargs -- optional arguments to pass to __init__ of the instatiated class
		"""
		 
		with self._lock:
			if not self._instance:
				self._instance = self._old_cls.__new__(cls)
				cls.__new__ = self.new_instantiated

		return self._instance

	def new_instantiated(self,  cls,  *args, **kwargs):
		""" Called to get an existing instance of a singleton.
		Keyword arguments:
		cls, args, kwargs -- ignored, exist for calling conventions only
		"""
		return self._instance

	def __call__(self):
		""" Produces a singleton.
		Returns a copy of the original class which has its __new__ method replaced by new_uninstantiated
		"""
		new_cls = type(self._old_cls.__name__,  self._old_cls.__bases__,  dict(self._old_cls.__dict__))
		new_cls.__new__ = self.new_uninstantiated
		return new_cls
			
def Singleton(cls):
		factory = SingletonFactory(cls,  _threading.RLock())
		return factory()
			
