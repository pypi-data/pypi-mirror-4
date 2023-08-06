# -*- coding: utf-8 -*-
# postcreate script. You could setup a workflow here for example
wf = add_workflow('workpackage workflow', 'Workpackage')
reserve = wf.add_state(_(u'not started'), initial=True)
encours = wf.add_state(_(u'in progress'))
attente = wf.add_state(_(u'client validation'))
recette = wf.add_state(_(u'validated'))
garantie = wf.add_state(_(u'warranty'))

wf.add_transition(_(u'start'), reserve, encours)
wf.add_transition(_(u'done'), encours, attente)
wf.add_transition(_(u'warrant'), attente, garantie)
wf.add_transition(_(u'validate'), garantie, recette)

wf = add_workflow('workcase workflow', 'Workcase')
ouvert  = wf.add_state(_(u'opened'), initial=True)
action  = wf.add_state(_('action'))
attente = wf.add_state(_('pending'))
succes = wf.add_state(_(u'success'))
echec = wf.add_state(_(u'failure'))

wf.add_transition(_(u'open'), (action, attente), ouvert)
wf.add_transition(_(u'action'), (attente, ouvert), action)
wf.add_transition(_(u'wait'), (ouvert, action), attente)
wf.add_transition(_(u'failed'), (ouvert, action, attente), echec)
wf.add_transition(_(u'done'), (ouvert, action, attente), succes)

