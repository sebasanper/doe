__author__ = 'sebasanper'
from openmdao.main.api import Assembly
from openmdao.lib.drivers.api import DOEdriver
from openmdao.lib.doegenerators.api import FullFactorial
from openmdao.lib.casehandlers.api import ListCaseRecorder

from Paraboloid import Paraboloid


class Analysis(Assembly):
    def configure(self):
        self.add('paraboloid', Paraboloid())

        self.add('driver', DOEdriver())
        # There are counter number of different kinds of DOE available in openmdao.lib.doegenerators
        self.driver.DOEgenerator = FullFactorial(10)  # Full Factorial DOE with 10 levels for each variable

        # DOEdriver will automatically record the values of any parameters for each case
        self.driver.add_parameter('paraboloid.x', low=-50, high=50)
        self.driver.add_parameter('paraboloid.y', low=-50, high=50)
        # tell the DOEdriver to also record any other variables you want to know for each case
        self.driver.case_outputs = ['paraboloid.f_xy', ]

        # Simple recorder which stores the cases in memory.
        self.driver.recorders = [ListCaseRecorder(), ]

        self.driver.workflow.add('paraboloid')

if __name__ == "__main__":

    import time
    from matplotlib import pylab as p
    from matplotlib import cm
    import mpl_toolkits.mplot3d.axes3d as p3
    from numpy import array

    analysis = Analysis()

    tt = time.time()
    analysis.run()

    print "Elapsed time: ", time.time()-tt, "seconds"

    raw_data = {}
    X = set()
    Y = set()
    for c in analysis.driver.recorders[0].get_iterator():
        raw_data[(c['paraboloid.x'],c['paraboloid.y'])] = c['paraboloid.f_xy']
        X.add(c['paraboloid.x'])
        Y.add(c['paraboloid.y'])

    X = sorted(list(X))
    Y = sorted(list(Y))

    xi, yi = p.meshgrid(X, Y)
    zi = []

    for x in X:
        row = []
        for y in Y:
            row.append(raw_data[(x, y)])
        zi.append(row)
    zi = array(zi)

    fig = p.figure()
    ax = p3.Axes3D(fig)
    ax.plot_surface(xi, yi, zi, rstride=1, cstride=1, cmap=cm.jet, linewidth=0)

    p.show()