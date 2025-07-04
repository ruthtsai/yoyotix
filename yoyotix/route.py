# route.py
class SupportRouter:
	#讀
	def db_for_read(model, **hint):
		if model._meta.app_label == 'support':
			return 'supportdb'

		return None
	#寫
	def db_for_write(model, **hint):
		if model._meta.app_label == 'support':
			return 'supportdb'

		return None

	def allow_relation(obj1, obj2, **hint):
		if obj1._meta.app_label == 'support' or obj2._meta.app_label == 'support':
			return True
		return None

	def allow_migrate(db, app_label, model_name=None, **hint):
		if app_label == 'support':
			return db =='supportdb'
		elif db =='supportdb':
			return False
		return None
