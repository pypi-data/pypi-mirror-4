from yams.buildobjs import (EntityType, SubjectRelation, ObjectRelation,
                            String, Date, Float, RichString)
from cubicweb.schema import RQLConstraint, WorkflowableEntityType

_ = unicode

class Order(WorkflowableEntityType):
    title = String(required=True, fulltextindexed=True, maxsize=128, unique=True)
    date = Date(description=_('date order was placed on'))
    split_into = SubjectRelation('WorkOrder', cardinality='*1', composite='subject')

    # computed attributes
    budget = Float(description=_('computed attribute'), required=True, default=0)
    progress_done = Float(description=_('computed attribute'))
    progress_todo = Float(description=_('computed attribute'))


class WorkOrder(WorkflowableEntityType):
    title = String(required=True, fulltextindexed=True, indexed=True, maxsize=128)
    description = RichString(fulltextindexed=True)
    budget = Float(description=_('amount that should not be overspent'))
    begin_date = Date(description=_('date work order will begin on'))
    end_date = Date(description=_('date work order will end on'))

    # computed attributes
    progress_done = Float(description=_('computed attribute'))
    progress_todo = Float(description=_('computed attribute'))
