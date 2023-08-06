from orm.datatypes import CustomType
from treedict import TreeDict
import json


class Serializer(object):
	def serialize(self):
		data = {}
		
		for key, value in self.data.iteritems():
			data_type = value.__class__.__name__
			data[key] = {
				'dataType': data_type,
				'required': key in self.model.required_fields,
				'options': value.get_options()
			}
		
		return data