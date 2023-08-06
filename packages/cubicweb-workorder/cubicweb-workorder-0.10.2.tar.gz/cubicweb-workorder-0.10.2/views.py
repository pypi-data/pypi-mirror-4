"""template-specific forms/views/actions/components"""

from cubicweb.selectors import is_instance
from cubicweb.web import uicfg
from cubicweb.web.views.ibreadcrumbs import IBreadCrumbsAdapter

class WorkOrderIBreadCrumbsAdapter(IBreadCrumbsAdapter):
    __select__ = is_instance('WorkOrder')

    def parent_entity(self):
        return self.entity.order

_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
_afs = uicfg.autoform_section

# Order
_pvs.tag_subject_of(('Order', 'split_into', '*'), 'relations')
_pvs.tag_attribute(('Order', 'budget'), 'hidden')
_pvs.tag_attribute(('Order', 'progress_done'), 'hidden')
_pvs.tag_attribute(('Order', 'progress_todo'), 'hidden')
_pvdc.tag_subject_of(('Order', 'split_into', '*'),
                     {'vid': 'ic_progress_table_view'})

_afs.tag_attribute(('Order', 'budget'), 'main', 'hidden')
_afs.tag_attribute(('Order', 'progress_todo'), 'main', 'hidden')
_afs.tag_attribute(('Order', 'progress_done'), 'main', 'hidden')
_afs.tag_subject_of(('Order', 'split_into', '*'), 'main', 'inlined')

# WorkOrder
_afs.tag_attribute(('WorkOrder', 'progress_todo'), 'main', 'hidden')
_afs.tag_attribute(('WorkOrder', 'progress_done'), 'main', 'hidden')
