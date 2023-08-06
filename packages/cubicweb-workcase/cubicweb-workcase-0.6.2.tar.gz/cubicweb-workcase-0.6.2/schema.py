# template's specific schema
from yams.buildobjs import EntityType, SubjectRelation, ObjectRelation, String, RichString
from cubicweb.schema import RQLConstraint, WorkflowableEntityType

class Workcase(WorkflowableEntityType):
    ref = String(required=True, fulltextindexed=True, indexed=True,
                 maxsize=16, unique=True)
    subject = String(fulltextindexed=True, maxsize=256)
    split_into = SubjectRelation('Workpackage', cardinality='*1',
                                 composite='subject')


class Workpackage(WorkflowableEntityType):
    title = String(required=True, fulltextindexed=True, indexed=True, maxsize=128)
    description = RichString(fulltextindexed=True)


