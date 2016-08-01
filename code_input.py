# -*- coding: utf-8 -*-

from webApp import db, Code

db.create_all()

code1 = Code('code1111', 1000)
code2 = Code('code2222', 2000)
code3 = Code('code3333', 3000)
code4 = Code('code4444', 1000)

db.session.add(code1)
db.session.add(code2)
db.session.add(code3)
db.session.add(code4)

db.session.commit()

result = Code.query.filter_by(sum=1000, code='code4444').all()
print result

# db.session.query(Code).filter(Code.id==1).update({Code.result:'using'})
# db.session.commit()

code1.code = 'code5555'
db.session.commit()

result = Code.query.filter_by(sum=1000).all()
print result
