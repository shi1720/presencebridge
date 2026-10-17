"""Executable local example: compile a tool, decode a wire request, update SQLite.
Run `python experiments/demo.py`; this does not contact external APIs.
"""
import json,sqlite3
from presencebridge import Codec
SCHEMA={
 'type':'object','properties':{
  'enabled':{'type':'boolean'},'note':{'type':['string','null']}
 },'required':[],'additionalProperties':False}

def apply_wire(db, codec, wire):
 # Decode and validate before beginning the write. No default-filling or
 # exclude_none serialization is allowed between this point and SQL binding.
 request=codec.decode(wire)
 with db:
  for key,value in request.items():
   if key not in ('enabled','note'):raise ValueError('Unknown backend column')
   db.execute(f'UPDATE customer SET "{key}"=? WHERE id=1',(value,))
 return db.execute('SELECT enabled,note FROM customer WHERE id=1').fetchone()

def main():
 db=sqlite3.connect(':memory:')
 db.execute('CREATE TABLE customer (id INTEGER PRIMARY KEY, enabled BOOLEAN, note TEXT)')
 db.execute('INSERT INTO customer VALUES (1,1,\'keep this note\')');db.commit()
 c=Codec(SCHEMA)
 for source in [{'enabled':False},{'note':None},{}]:
  wire=c.encode(source);state=apply_wire(db,c,wire)
  print(json.dumps(dict(source=source,wire=wire,decoded=c.decode(wire),state=dict(enabled=bool(state[0]),note=state[1]))))
 db.close()
if __name__=='__main__':main()
