import pstats
p = pstats.Stats('network.prof')
p.strip_dirs().sort_stats('time').print_stats(40)
# p.strip_dirs().sort_stats('cumulative').print_stats(40)
