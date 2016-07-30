# -*- coding: utf-8 -*-

from webApp import db, Code

db.create_all()

code1 = Code('code1111', 1000)
code2 = Code('code2222', 2000)
code3 = Code('code3333', 3000)

db.session.add(code1)
db.session.add(code2)
db.session.add(code3)

db.session.commit()

# db.session.query(Code).filter(Code.id==1).update({Code.result:'using'})
# db.session.commit()

result = Code.query.all()
print result
