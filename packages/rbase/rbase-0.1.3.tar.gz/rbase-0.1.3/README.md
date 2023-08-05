rbase
=====

A redis base class.

Usage
-----

	>>> class MyTodo(rbase.Base):
	>>> 	def __init__(description):
	>>> 		self.description = description
	>>> todo = MyTodo("Go to the store")
	>>> todo.save()
	<class 'rbase.base.Base'>(Base:1)
	
	>>> todo = MyTodo.get(1)
	>>> todo.description
	"Go to the store"
	
	>>> todo_two = MyTodo("Pick up milk")
	>>> todo_two.save()
	<class 'rbase.base.Base'>(Base:2)
	
	>>> todos = MyTodo.all()
	[<class 'rbase.base.Base'>(Base:1), <class 'rbase.base.Base'>(Base:2)]
	