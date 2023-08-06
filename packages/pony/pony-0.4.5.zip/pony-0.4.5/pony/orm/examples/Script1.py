from pony.orm import *
db = Database('sqlite', ':memory:')
class Post(db.Entity):
    name = Required(unicode)
    content = Required(LongUnicode)
    tags = Set("Tag")

class Tag(db.Entity):
    name = PrimaryKey(unicode)
    posts = Set("Post")

sql_debug(True)
db.generate_mapping(create_tables=True)
t1 = Tag(name="tag1")
t2 = Tag(name="tag2")
t3 = Tag(name="tag3")
p1 = Post(name="Post1", content="...")
p2 = Post(name="Post2", content="...", tags=[t2, t3])
commit()
rollback()

t = None
posts = select(p for p in Post if t in p.tags)[:]
posts = select(p for p in Post if JOIN(t in p.tags))[:]

