from dataclasses import field, dataclass

from marshmallow import EXCLUDE, Schema
from marshmallow_dataclass import class_schema


class PermissionsMetaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    def SetAll(self, value: bool) -> "PermissionsMetaSchema":
        for field_name, field_value in self.__dataclass_fields__.items():   # type: ignore [attr-defined]
            if isinstance(getattr(self, field_name), bool):
                setattr(self, field_name, value)
            elif hasattr(getattr(self, field_name), '__dataclass_fields__'):
                nested_obj = getattr(self, field_name)
                nested_obj.SetAll(value)
        return self


@dataclass
class Permission(PermissionsMetaSchema):
    value: bool = field(metadata=dict(data_key='value'))
    description: str = field(metadata=dict(data_key='description'))

    def __bool__(self):
        return self.value


@dataclass
class LessonsEdit(PermissionsMetaSchema):
    homework: Permission = field(metadata=dict(data_key='homework'))
    photo: Permission = field(metadata=dict(data_key='photo'))
    url: Permission = field(metadata=dict(data_key='url'))


@dataclass
class Lessons(PermissionsMetaSchema):
    use: Permission = field(metadata=dict(data_key='use'))
    edit: LessonsEdit = field(metadata=dict(data_key='edit'))


@dataclass
class Schedule(PermissionsMetaSchema):
    use: Permission = field(metadata=dict(data_key='use'))
    edit: Permission = field(metadata=dict(data_key='edit'))


@dataclass
class ScheduleCall(PermissionsMetaSchema):
    use: Permission = field(metadata=dict(data_key='use'))
    edit: Permission = field(metadata=dict(data_key='edit'))


@dataclass
class ScheduleExam(PermissionsMetaSchema):
    use: Permission = field(metadata=dict(data_key='use'))
    edit: Permission = field(metadata=dict(data_key='edit'))


@dataclass
class AdminPanelUse(PermissionsMetaSchema):
    server_status: Permission = field(metadata=dict(data_key='server_status'))
    newsletter: Permission = field(metadata=dict(data_key='newsletter'))
    role: Permission = field(metadata=dict(data_key='role'))


@dataclass
class AdminPanel(PermissionsMetaSchema):
    use: AdminPanelUse = field(metadata=dict(data_key='use'))


@dataclass
class Permissions(PermissionsMetaSchema):
    lessons: Lessons = field(metadata=dict(data_key='lessons'))
    schedule: Schedule = field(metadata=dict(data_key='schedule'))
    schedule_call: ScheduleCall = field(metadata=dict(data_key='schedule_call'))
    schedule_exam: ScheduleExam = field(metadata=dict(data_key='schedule_exam'))
    admin_panel: AdminPanel = field(metadata=dict(data_key='admin_panel'))
    admin: Permission = field(metadata=dict(data_key='admin'))


PermissionSchema = class_schema(Permission)
PermissionsSchema = class_schema(Permissions)
LessonsSchema = class_schema(Lessons)
LessonsEditSchema = class_schema(LessonsEdit)
ScheduleSchema = class_schema(Schedule)
AdminPanelSchema = class_schema(AdminPanel)
AdminPanelUseSchema = class_schema(AdminPanelUse)
