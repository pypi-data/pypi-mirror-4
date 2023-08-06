import re
import types
import inspect

class inner(object):
	def __init__(self, cls, obj):
		mro = type(obj).__mro__
		i = mro.index(cls)
		
		if not i:
			raise TypeError("inner(type, obj): obj must be an instance of a subtype of type")
		
		self._mro = list(reversed(mro[:i]))
		self._obj = obj
	
	def __getattr__(self, name):
		att = None
		
		for t in self._mro:
			raw_att = getattr(t, name)
			
			if not raw_att:
				continue
			
			if isinstance(raw_att, types.FunctionType):
				att = raw_att.__get__(self._obj, t)
			elif isinstance(raw_att, BetaMethod):
				att = raw_att.__get__(self._obj, t, inner = True)
			
			if att:
				break
		
		if att is None:
			raise TypeError("inner(type, obj): no inner method found")
		
		if isinstance(att, property):
			att = att()
		
		setattr(self, name, att)
		
		return att

class BoundBetaMethod(object):
	def __init__(self, method, obj, cls, up = False):
		raw_meth = None
		
		mro = obj.__class__.__mro__
		i = mro.index(cls)
		meth_name = method.func_name
		
		if up:
			mro_part = mro[i:]
		else:
			mro_part = reversed(mro[:i + 1])
		
		for cls in mro_part:
			raw_meth = getattr(cls, meth_name, None)
			
			if raw_meth is None:
				continue
			
			if up:
				if isinstance(raw_meth, (types.FunctionType, BetaMethod)):
					break
			else:
				if isinstance(raw_meth, BetaMethod):
					if not raw_meth._mock:
						break
		
		if raw_meth is None:
			raw_meth = getattr(mro[-1], meth_name)
		
		self.im_func = raw_meth.im_func
		self.im_self = obj
	
	def __call__(self, *args, **kwargs):
		return self.im_func(self.im_self, *args, **kwargs)

class BetaMethod(object):
	def __init__(self, im_func, mock = False):
		# `mock` is used so that the method on the most recent subclass
		# doesn't get called during an external dispatch. If there is
		# beta method in the hierarchy, the _lowest_ beta method is the
		# target of an external dispatch.
		self.im_func = im_func
		self._mock = mock
	
	def __call__(self, *args, **kwargs):
		return self.im_func(*args, **kwargs)
	
	def __get__(self, obj, type, inner = False):
		if obj is None:
			return self
		
		cls = obj.__class__
		imc = self.im_class
		
		up = False
		
		if inner:
			# inner dispatch
			pass
		elif type == cls:
			if cls == imc:
				# external dispatch
				type = object
			elif issubclass(cls, imc):
				# super dispatch
				up = True
				type = imc
			else:
				raise self._dispatch_error(type, cls, imc)
		elif type == imc and issubclass(cls, type):
			# inner dispatch
			pass
		else:
			raise self._dispatch_error(type, cls, imc)
		
		return BoundBetaMethod(self, obj, type, up = up)
	
	@property
	def func_name(self):
		return self.im_func.func_name
	
	def _dispatch_error(self, type, cls, imc):
		return Exception(u"Can't tell what kind of dispatch to bind for: {}, {}, {}".format(
			type, cls, imc
		))

class BetaMetaclass(type):
	def __new__(cls, name, bases, attrs):
		newattrs = {}
		
		betamethods = set()
		for base in bases:
			for v in base.__dict__.values():
				if isinstance(v, BetaMethod):
					betamethods.add(v.func_name)
		
		bms = []
		for k, v in attrs.items():
			if isinstance(v, types.FunctionType):
				should_be_beta = cls._should_be_beta(v)
				
				if should_be_beta:
					v = BetaMethod(v)
				elif k in betamethods:
					v = BetaMethod(v, True)
			
			if isinstance(v, BetaMethod):
				bms.append(v)
			
			newattrs[k] = v
		
		kls = type.__new__(cls, name, bases, newattrs)
		
		for meth in bms:
			meth.im_class = kls
		
		return kls
	
	@classmethod
	def _should_be_beta(cls, m):
		# TODO: So incredibly hacky.
		# Need to deduce if the method is a betamethod by looking if it calls
		# 'inner', but the only way to do this other than looking at the source
		# is to make the Python compiler aware of 'inner' semantics.
		src = inspect.getsource(m)
		# TODO: False positive if method contains strings containing "inner("
		return bool(re.search(r'([^\.]|^)\binner\s*\(', src))

def test():
	_test_short()
	_test_long()

def _test_short():
	class A(object):
		def f(self):
			l = [4]
			return l
	
	class B(A):
		__metaclass__ = BetaMetaclass
		
		def f(self):
			l = [1]
			l.extend(inner(B, self).f())
			l.extend([3])
			l.extend(super(B, self).f())
			return l
	
	class C(B):
		def f(self):
			l = [2]
			return l
	
	obj = C()
	assert tuple(obj.f()) == tuple(xrange(1, 5))

def _test_long():
	class A(object):
		__metaclass__ = BetaMetaclass
		
		def y(self):
			l = [3]
			return l

	class B(A):
		def y(self):
			l = [2]
			l.extend(super(B, self).y())
			return l

	class C(B):
		def y(self):
			l = [1]
			l.extend(super(C, self).y())
			l.extend(inner(C, self).y())
			return l

	class D(C):
		def y(self):
			return [5]

	class E(D):
		def y(self):
			l = [4]
			l.extend(super(E, self).y())
			l.extend(inner(E, self).y())
			return l

	class F(E):
		def y(self):
			l = [7]
			return l

	class G(F):
		def y(self):
			l = [6]
			l.extend(super(G, self).y())
			return l
	
	obj = G()
	assert tuple(obj.y()) == tuple(xrange(1, 8))

if __name__ == '__main__':
	test()
