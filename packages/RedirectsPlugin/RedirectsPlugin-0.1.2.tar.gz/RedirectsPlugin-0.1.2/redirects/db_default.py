from trac.db import Table, Column, Index

version = 1
name = 'redirects'

schema = [
	Table('redirects', key='from')[
		Column('frompath', type='text'),
		Column('topath', type='text'),
		Column('enabled', type='int')],
]
