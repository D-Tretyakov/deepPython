from list_mul import mult
import cProfile, pstats, io

pr = cProfile.Profile()
pr.enable()
for i in range(100):
    mult(list(range(1, 101)))
pr.disable()

s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())