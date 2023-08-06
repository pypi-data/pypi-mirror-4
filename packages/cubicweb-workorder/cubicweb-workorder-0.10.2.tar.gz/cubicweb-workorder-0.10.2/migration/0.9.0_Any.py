for e in rql('Any X WHERE X progress_target NULL').entities():
    e.update_progress() # will be recomputed according to budget

drop_attribute('WorkOrder', 'progress_target')
