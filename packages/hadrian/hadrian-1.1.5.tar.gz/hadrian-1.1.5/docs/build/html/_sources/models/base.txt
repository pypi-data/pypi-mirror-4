===========
Base Models
===========

Audit Base
==========

Hadrian now includes a base models module with a base model of AuditBase. Audit base added created_on and updated_on fields to each model that inherits from it. To use it simply::


    from kstate.common.models.base import AuditBase

    class SomeModel(AuditModel):
        some_field = models.BooleanField()
