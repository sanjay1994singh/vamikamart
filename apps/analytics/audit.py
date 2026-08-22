from .models import AuditLog


class AuditService:
    @staticmethod
    def log(action, entity, object_id="", actor=None, previous=None, new=None, ip_address=None):
        return AuditLog.objects.create(
            actor=actor,
            action=action,
            entity=entity,
            object_id=str(object_id or ""),
            previous_value=previous or {},
            new_value=new or {},
            ip_address=ip_address,
        )
