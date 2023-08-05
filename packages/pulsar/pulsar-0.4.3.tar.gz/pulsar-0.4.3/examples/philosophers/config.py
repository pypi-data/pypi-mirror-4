
def arbiter_task(arbiter):
    import objgraph
    EVERY = 299
    #
    last_show = arbiter.local.get('objgraph') or 0
    if not last_show:
        #objgraph.show_most_common_types()
        arbiter.log.error('Arbiter loops %s' % arbiter.ioloop.num_loops)
        objgraph.show_growth(limit=10)
    last_show += 1
    if last_show > EVERY:
        last_show = 0
    arbiter.local['objgraph'] = last_show