"""workorder hooks: compute progress"""

__docformat__ = "restructuredtext en"

from cubicweb.selectors import is_instance
from cubicweb.server import hook

WORKORDER_FINAL_STATES = set( (u'done',) )

class UpdateProgressOp(hook.DataOperationMixIn, hook.Operation):
    def precommit_event(self):
        for eid, compute in self.get_data():
            entity = self.session.entity_from_eid(eid)
            entity.update_progress(compute)


class UpdateProgressOnWorkOrderStatusChange(hook.Hook):
    """when a ticket status change and it's identical to another one, change the
    state of the other one as well
    """
    __regid__ = 'workorder.progress.status_change'
    __select__ = hook.Hook.__select__ & is_instance('TrInfo')
    events = ('after_add_entity',)
    def __call__(self):
        trinfo = self.entity
        forentity = trinfo.for_entity
        if forentity.e_schema == 'WorkOrder' \
                and trinfo.new_state.name in WORKORDER_FINAL_STATES:
            forentity.set_attributes(progress_todo=0)


class UpdateProgressOnWorkOrderModification(hook.Hook):
    __regid__ = 'workorder.progress.workorder'
    __select__ = hook.Hook.__select__ & is_instance('WorkOrder')
    events = ('before_add_entity', 'before_update_entity', )

    def __call__(self):
        edited = self.entity.cw_edited
        if 'budget' in edited:
            if self.entity.progress_done is None:
                edited['progress_done'] = 0
            if self.entity.progress_todo is None:
                edited['progress_todo'] = edited['budget']
            UpdateProgressOp.get_instance(self._cw).add_data(
                (self.entity.eid, False) )
        elif 'progress_todo' in edited or 'progress_done' in edited:
            UpdateProgressOp.get_instance(self._cw).add_data(
                (self.entity.eid, False) )


class UpdateProgressOnSplitIntoChange(hook.Hook):
    __regid__ = 'workorder.progress.split_into'
    __select__ = (hook.Hook.__select__
                  & hook.match_rtype('split_into', frometypes=('Order',)))
    events = ('after_add_relation', 'after_delete_relation',)

    def __call__(self):
        UpdateProgressOp.get_instance(self._cw).add_data( (self.eidfrom, True) )

