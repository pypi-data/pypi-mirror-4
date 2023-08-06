#from pony.orm.examples.estore import *
# result = select((c, count(c.orders.items), c.orders.items.product.name) for c in Customer)[:]
#result = select(c for c in Customer if c.name.startswith('A')).order_by(Customer.name)[:2]
#print result

#from pony.orm.examples.inheritance1 import *
#select(s for s in Student if s.mentor.salary == 1000)[:]

from pony.orm.examples.estore import *
c = Category.get(name='Tablets')
c2 = Category.get(name='Tablets')


