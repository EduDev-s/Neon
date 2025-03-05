from json import loads as json_loads

from other.log.colors import blue
from other.log.logging import logging
from other.PermissionsManager.models import Permissions, PermissionsSchema


class PermissionsManager:
    log = logging(Name='PM', Color=blue)

    DefaultConfigPermissions: dict = None

    DefaultPermissions: Permissions = None
    OwnerPermissions: Permissions = None

    def __init__(self):
        try:
            self.log.init('Initialization PermissionsManager is started')

            self.DefaultConfigPermissions: dict = json_loads(open('./other/permissions.json', 'r').read())
            self.log.init('permissions.json is loaded')

            self.DefaultPermissions = self.JSONToClass(None, self.DefaultConfigPermissions)
            self.log.init('Default permissions (JSON) converted to Class (Permissions)')

            self.OwnerPermissions = self.JSONToClass(None, self.DefaultConfigPermissions)
            self.OwnerPermissions.SetAll(True)
            self.log.init('Owner permissions (JSON) converted to Class (Permissions)')

            self.log.init('Initialization PermissionsManager is completed')
        except FileNotFoundError:
            self.log.cerror(None, 'File \'permissions.json\' not found!')
            exit(1)

    def JSONToClass(self, user_id: int | None, p: dict) -> Permissions:
        try:
            self.log.debug(user_id, 'Convert JSON in Permissions is started')

            data = {
                'lessons': p['permissions']['lessons'],
                'schedule': p['permissions']['schedule'],
                'schedule_call': p['permissions']['schedule_call'],
                'schedule_exam': p['permissions']['schedule_exam'],
                'admin_panel': p['permissions']['admin_panel'],
                'admin': p['permissions']['admin']
            }
            permissions_schema = PermissionsSchema()
            permissions_obj = permissions_schema.load(data)

            self.log.debug(user_id, 'Convert JSON in Permissions is completed')
            return permissions_obj

        except Exception as Error:
            self.log.error(user_id, str(Error))
            return Error

    def ClassToJSON(self, user_id: int | None, permissions: Permissions) -> dict | Exception:
        try:
            self.log.debug(user_id, 'Convert Permissions in JSON is started')

            permissions_schema = PermissionsSchema()
            json = permissions_schema.dump(permissions)

            self.log.debug(user_id, 'Convert Permissions in JSON is completed')
            return {'permissions': json}

        except Exception as Error:
            self.log.error(user_id, str(Error))
            return Error

    def Combine(self, user_id: int | None, obj_1: Permissions, obj_2: Permissions) -> Permissions:
        """
        The two classes of Permissions impoverishes.
        If in at least one of the objects field == true, then in the source object it will also be == True
        """

        try:
            dict_1 = self.ClassToJSON(user_id, obj_1)
            dict_2 = self.ClassToJSON(user_id, obj_2)

            def merge_dicts(dict1, dict2):
                merged = {}

                for key in dict1:
                    if key in dict2:
                        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                            merged[key] = merge_dicts(dict1[key], dict2[key])
                        else:
                            merged[key] = dict1[key] or dict2[key]
                    else:
                        merged[key] = dict1[key]

                for key in dict2:
                    if key not in merged:
                        merged[key] = dict2[key]

                return merged

            return self.JSONToClass(user_id, merge_dicts(dict_1, dict_2))
        except Exception as Error:
            self.log.error(user_id, f'{Error}')
            return Error


PM = PermissionsManager()
