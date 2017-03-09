from openmdao.main.api import Assembly
from openmdao.lib.drivers.api import CaseIteratorDriver, DOEdriver
from openmdao.lib.doegenerators.api import Uniform
from openmdao.lib.casehandlers.api import ListCaseRecorder, ListCaseIterator, ExprCaseFilter

from openmdao.examples.simple.paraboloid import Paraboloid


class Analysis(Assembly):

    def configure(self):
        self.add('paraboloid', Paraboloid())
        doe = self.add('driver', DOEdriver())
        doe.DOEgenerator = Uniform(num_samples=1000)
        doe.add_parameter('paraboloid.x', low=-50, high=50)
        doe.add_parameter('paraboloid.y', low=-50, high=50)
        doe.case_outputs = ['paraboloid.f_xy']
        doe.workflow.add('paraboloid')


if __name__ == '__main__':

    analysis = Analysis()

    # Run full experiment and record results.
    recorder = ListCaseRecorder()
    analysis.driver.recorders = [recorder]
    analysis.run()

    # Reconfigure driver.
    workflow = analysis.driver.workflow
    analysis.add('driver', CaseIteratorDriver())
    analysis.driver.workflow = workflow

    # Rerun cases where paraboloid.f_xy <= 0.
    analysis.driver.iterator = recorder.get_iterator()
    analysis.driver.filter = ExprCaseFilter("case['paraboloid.f_xy'] <= 0")
    analysis.run()

    # Rerun cases which failed.
    analysis.driver.iterator = recorder.get_iterator()
    analysis.driver.filter = ExprCaseFilter("case.msg")
    analysis.run()