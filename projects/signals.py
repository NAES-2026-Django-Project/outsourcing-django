from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, Stage, StageType

ESTAGIOS_PADRAO = (
    ('Backlog', StageType.BACKLOG),
    ('Em andamento', StageType.DOING),
    ('Concluído', StageType.DONE),
    ('Aprovado', StageType.APPROVED),
)


@receiver(post_save, sender=Project)
def criar_estagios_padrao(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        Stage.objects.bulk_create(
            Stage(project=instance, name=nome, stage_type=tipo, order=ordem)
            for ordem, (nome, tipo) in enumerate(ESTAGIOS_PADRAO, start=1)
        )
