from datetime import date

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import IMileStoneAdapter, IProgressAdapter
from cubicweb.selectors import is_instance

class Order(AnyEntity):
    __regid__ = 'Order'
    fetch_attrs, fetch_order = fetch_config(('title', 'date'))

    def update_progress(self, compute=True):
        """callable only on the server side"""
        if compute:
            workorders = self.split_into
            self.set_attributes(
                budget=sum(wod.budget or 0 for wod in workorders),
                progress_done=sum(wod.progress_done or 0 for wod in workorders),
                progress_todo=sum(wod.progress_todo or 0 for wod in workorders))


class WorkOrder(AnyEntity):
    __regid__ = 'WorkOrder'

    fetch_attrs, fetch_order = fetch_config(('title', 'description_format',
                                             'description', 'budget',
                                             'begin_date', 'end_date', 'in_state'))

    def dc_title(self):
        return self.title

    def dc_long_title(self):
        return u'%s - %s' % (self.order.dc_title(), self.title)

    @property
    def order(self):
        return self.reverse_split_into[0]

    def update_progress(self, compute=True):
        """callable only on the server side"""
        for order in self.reverse_split_into:
            order.update_progress(True)


class WorkOrderIMileStoneAdapter(IMileStoneAdapter):
    __select__ = is_instance('WorkOrder')
    parent_type = 'Order'

    def get_main_task(self):
        return self.entity.order

    def initial_prevision_date(self):
        """returns the initial expected end of the milestone"""
        return date.today()

    def eta_date(self):
        """returns expected date of completion based on what remains
        to be done
        """
        return date.today()

    def completion_date(self):
        """returns date on which the subtask has been completed"""
        return date.today()

    def contractors(self):
        """returns the list of persons supposed to work on this task"""
        return []

    def in_progress(self):
        return self.entity.cw_adapt_to('IWorkflowable').state == u'in progress'

    def progress_info(self):
        return {'estimated': self.entity.budget,
                'estimatedcorrected': self.entity.budget,
                'done': self.entity.progress_done,
                'todo': self.entity.progress_todo,}


# XXX IMileStone / IProgress inheritance stink
class WorkOrderProgressAdapter(WorkOrderIMileStoneAdapter):
    __regid__ = 'IProgress'
    __select__ = is_instance('WorkOrder')

class OrderProgressAdapter(IProgressAdapter):
    __select__ = is_instance('Order')

    def progress_info(self):
        return {'estimated': self.entity.budget,
                'estimatedcorrected': self.entity.budget,
                'done': self.entity.progress_done,
                'todo': self.entity.progress_todo,
                }

    def in_progress(self):
        return True # FIXME


class OrderIMileStoneAdapter(IMileStoneAdapter):
    __select__ = is_instance('Order')

    def get_main_task(self):
        return self.entity

    def initial_prevision_date(self):
        """returns the initial expected end of the milestone"""
        return date.today()

    def eta_date(self):
        """returns expected date of completion based on what remains
        to be done
        """
        return date.today()

    def completion_date(self):
        """returns date on which the subtask has been completed"""
        return date.today()

    def contractors(self):
        """returns the list of persons supposed to work on this task"""
        return []

    def in_progress(self):
        return self.entity.cw_adapt_to('IWorkflowable').state == u'in progress'

    def progress_info(self):
        return {'estimated': self.entity.budget,
                'estimatedcorrected': self.entity.budget,
                'done': self.entity.progress_done,
                'todo': self.entity.progress_todo,}
