from flask import jsonify


class JqGrid(object):

    def __init__(self, model, pager_id = None, extra_config = {},
                 data_url = None, caption = None, fields =  None, distinct = True):
        self.model = model
        self.pager_id = pager_id
        self.extra_config = extra_config
        self.data_url = data_url
        self.caption = caption
        self.fields =  fields
        self.distinct = distinct


    def get_default_config(self):
        config = {
            'datatype': 'json',
            'autowidth': True,
            'forcefit': True,
            'shrinkToFit': True,
            'jsonReader': { 'repeatitems': False,
                            'page':'page',
                            'total':'total_pages',
                            'records':'num_results',
                            'root':'objects'
                          },
            'rowNum': 10,
            'rowList': [10, 25, 50, 100],
            'sortname': 'id',
            'viewrecords': True,
            'sortorder': "asc",
            'pager': self.pager_id,
            'altRows': True,
            'gridview': True,
            'height': 'auto',
            'editurl':"/",
        }
        return config

    def get_config(self):
        config = self.get_default_config()
        config.update(self.extra_config)
        config.update({'url':self.data_url})
        config.update({'caption':self.caption})
        colNames, colModel = self.get_Col_Model_Name()
        config.update({'colNames':colNames})
        config.update({'colModel':colModel})
        config = jsonify(config)
        return config

    def get_Col_Model_Name(self):
        colNames = []
        colModel = []
        if not self.fields:
            if hasattr(self, 'model') and self.model is not None:
                for field in self.model.__table__.columns._data:
                    field_dict = {}
                    colNames.append(field)
                    field_dict['name'] = field
                    field_dict['index'] = field
                    field_dict['width'] = 90
                    colModel.append(field_dict)



            elif hasattr(self, 'model') and self.model is not None:
                fields = self.model[0].__table__.columns._data.keys()
            else:
                raise AttributeError("No queryset or model defined.")


        return colNames, colModel








