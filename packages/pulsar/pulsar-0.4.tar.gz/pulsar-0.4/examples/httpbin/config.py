
def __worker_task(actor):
    import objgraph
    EVERY = 9
    #
    last_show = actor.local.get('objgraph') or 0
    if not last_show:
        #objgraph.show_most_common_types()
        actor.log.error('io loops %s' % actor.ioloop.num_loops)
        objgraph.show_growth(limit=10)
    last_show += 1
    if last_show > EVERY:
        last_show = 0
    actor.local['objgraph'] = last_show
    
    
def arbiter_task(actor):
    import objgraph
    EVERY = 9
    #
    last_show = actor.local.get('objgraph') or 0
    if not last_show:
        #objgraph.show_most_common_types()
        actor.log.error('io loops %s' % actor.ioloop.num_loops)
        objgraph.show_growth(limit=10)
    last_show += 1
    if last_show > EVERY:
        last_show = 0
    actor.local['objgraph'] = last_show