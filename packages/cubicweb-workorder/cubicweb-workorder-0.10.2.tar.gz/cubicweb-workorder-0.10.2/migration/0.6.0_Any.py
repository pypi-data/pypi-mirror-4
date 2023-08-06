# add attributes
add_attribute('Order','budget')
for attr in ('progress_target', 'progress_done', 'progress_todo'):
    add_attribute('Order', attr)
    add_attribute('WorkOrder', attr)
checkpoint()

from logilab.common.shellutils import ProgressBar
workorders = rql('Any X WHERE X is WorkOrder', ask_confirm=False)
bar = ProgressBar(len(workorders), title='Updating progress information ')
bar.refresh()
for entity in workorders.entities():
    entity.update_progress()
    bar.update()
print
checkpoint()

# add states
reserve = rql('Any S WHERE S is State, S name "not started", '
              'S state_of W, W name "WorkOrder"', ask_confirm=False)[0][0]
annule = add_state(_(u'canceled'), 'WorkOrder')
add_transition(_(u'cancel'), 'WorkOrder', (reserve,), annule)

planned = rql('Any S WHERE S is State, S name "planned", '
              'S state_of W, W name "Order"', ask_confirm=False)[0][0]
sent = rql('Any S WHERE S is State, S name "sent", '
           'S state_of W, W name "Order"', ask_confirm=False)[0][0]
canceled = add_state(_(u'canceled'), 'Order')
add_transition(_(u'cancel'), 'Order', (planned,sent), canceled)
checkpoint()
