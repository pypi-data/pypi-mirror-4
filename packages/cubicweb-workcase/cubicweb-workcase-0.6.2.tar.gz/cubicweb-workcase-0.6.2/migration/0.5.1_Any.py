rql('SET S name "pending" WHERE S name "waited", S state_of W, W name "workcase workflow"')
rql('SET S allowed_transition T WHERE S name "opened", S state_of W, W name "workcase workflow", '
    'T transition_of W, T name "failed"')
rql('SET S allowed_transition T WHERE S name "action", S state_of W, W name "workcase workflow", '
    'T transition_of W, T name "wait"')
rql('SET S allowed_transition T WHERE S name "action", S state_of W, W name "workcase workflow", '
    'T transition_of W, T name "done"')
rql('SET S allowed_transition T WHERE S name "pending", S state_of W, W name "workcase workflow", '
    'T transition_of W, T name "done"')
checkpoint()
