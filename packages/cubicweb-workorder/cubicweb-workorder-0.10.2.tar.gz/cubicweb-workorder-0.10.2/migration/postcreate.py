# postcreate script. You could setup a workflow here for example

# XXX missing correct permissions configuration

# WorkOrder workflow
wwf = add_workflow(_('default workorder workflow'), 'WorkOrder')

reserve = wwf.add_state(_(u'not started'), initial=True)
encours = wwf.add_state(_(u'in progress'))
attente = wwf.add_state(_(u'client validation'))
garantie = wwf.add_state(_(u'warranty'))
recette = wwf.add_state(_(u'validated'))
annule = wwf.add_state(_(u'canceled'))

wwf.add_transition(_(u'cancel'), (reserve,), annule)
wwf.add_transition(_(u'start'), (reserve,), encours)
wwf.add_transition(_(u'done'), (encours,), attente)
wwf.add_transition(_(u'warrant'), (attente,), garantie)
wwf.add_transition(_(u'validated'), (attente, garantie), recette)


# Order workflow
owf = add_workflow(_('default order workflow'), 'Order')

planned = owf.add_state(_(u'planned'), initial=True)
canceled = owf.add_state(_(u'canceled'))
sent = owf.add_state(_(u'sent'))
in_progress = owf.add_state(_(u'in progress'))
done = owf.add_state(_(u'done'))
owf.add_transition(_(u'cancel'), (planned,sent), canceled)
owf.add_transition(_(u'send'), (planned,), sent)
owf.add_transition(_(u'receive'), (sent,), in_progress)
owf.add_transition(_(u'done'), (in_progress,), done)
