# assembler.py

import sys
import os
import logging

from abc import ABC
from datetime import datetime


from .config import Config, has_config
from .visualiser import Visualiser
from .stage import Estimator, Stage, Filter, Validator

LOGGER = logging.getLogger(__name__)


class Assembler(ABC):
    """
    Class responsible for assembling and executing a Surround pipeline.

    Responsibilities:

    - Encapsulate the configuration data and pipeline stages
    - Load configuration from a specified module
    - Run the pipeline with input data in predict/batch/train mode

    For more information on this process, see the :ref:`about` page.

    Example::

        assembler = Assembler("Example pipeline")
        assembler.set_stages([PreFilter(), PredictStage(), PostFilter()])
        assembler.init_assembler(batch_mode=False)

        data = AssemblyState("some data")
        assembler.run(data, is_training=False)

    Batch-predict mode::

        assembler.init_assembler(batch_mode=True)
        assembler.run(data, is_training=False)

    Training mode::

        assembler.init_assembler(batch_mode=True)
        assembler.run(data, is_training=True)

    Predict/Estimate mode::

        assembler.init_assembler(batch_mode=False)
        assembler.run(data, is_training=False)
    """

    # pylint: disable=too-many-instance-attributes
    @has_config
    def __init__(self, assembler_name="", config=None):
        """
        Constructor for an Assembler pipeline:

        :param assembler_name: The name of the pipeline
        :param config: Surround Config object
        :type assembler_name: str
        """
        self.assembler_name = assembler_name
        self.config = config
        self.stages = None
        self.batch_mode = False
        self.finaliser = None

    def init_assembler(self, batch_mode=False):
        """
        Initializes the assembler and all of it's stages.

        Calls the :meth:`surround.stage.Stage.initialise` method of all stages and the estimator.

        .. note:: Should be called after :meth:`surround.assembler.Assembler.set_estimator` and
                :meth:`surround.assembler.Assembler.set_config`.

        :param batch_mode: Whether batch mode should be used
        :type batch_mode: bool
        :returns: whether the initialisation was successful
        :rtype: bool
        """

        self.batch_mode = batch_mode
        try:
            if self.stages:
                for stage in self.stages:
                    stage.initialise(self.config)

            if self.finaliser:
                self.finaliser.initialise(self.config)
        except Exception:
            LOGGER.exception("Failed initiating Assembler")
            return False

        return True

    def run(self, state=None, is_training=False):
        """
        Run the pipeline using the input data provided.

        If ``is_training`` is set to ``True`` then when it gets to the execution of the estimator,
        it will use the :meth:`surround.stage.Estimator.fit` method instead.

        If ``surround.enable_stage_output_dump`` is enabled in the Config instance then each filter and
        estimator's :meth:`surround.stage.Stage.dump_output` method will be called.

        This method doesn't return anything, instead results should be stored in the ``state``
        object passed in the parameters.

        :param state: Data passed between each stage in the pipeline
        :type state: :class:`surround.State`
        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """

        LOGGER.info("Starting '%s'", self.assembler_name)

        if not self.stages:
            raise ValueError("There are no stages to run!")

        if not state:
            raise ValueError("state is required to run an assembler")
        self.state = state

        state.freeze()

        def _run_stage_safe(a_stage):
            start_time = datetime.now()
            try:
                if isinstance(a_stage, Estimator):
                    a_stage.fit(state, self.config) if is_training else a_stage.estimate(state, self.config)
                elif isinstance(a_stage, Validator):
                    a_stage.validate(state, self.config)
                else:
                    a_stage.operate(state, self.config)
            except Exception as e:
                if self.config.get_path("surround.surface_exceptions"):
                    raise e
                else:
                    state.errors.append(str(e))
                LOGGER.exception(e)
            execution_time = datetime.now() - start_time
            state.execution_time.append(str(execution_time))
            LOGGER.info("%s took %s secs", type(a_stage).__name__, execution_time)

        for stage in self.stages:
            _run_stage_safe(stage)
            if state.errors:
                break

        if self.finaliser:
            _run_stage_safe(self.finaliser)

        if state.errors:
            LOGGER.error(state.errors)

        state.thaw()

    def load_config(self, module):
        """
        Given a module contained in the root of the project, create an instance of
        :class:`surround.config.Config` loading configuration data from the ``config.yaml``
        found in the project, and use this configuration for the pipeline.

        .. note:: Should be called before :meth:`surround.assembler.Assemble.init_assembler`

        :param module: name of the module
        :type module: str
        """

        if module:
            # Module already imported and has a file attribute
            mod = sys.modules.get(module)
            if mod and hasattr(mod, '__file__'):
                package_path = os.path.dirname(os.path.abspath(mod.__file__))
                root_path = os.path.dirname(package_path)
            else:
                raise ValueError("Invalid Python module %s" % module)

            self.set_config(Config(root_path))

            if not os.path.exists(self.config["output_path"]):
                os.makedirs(self.config["output_path"])
        else:
            self.set_config(Config())

        return self

    def set_config(self, config):
        """
        Set the configuration data to be used during pipeline execution.

        .. note:: Should be called before :meth:`surround.assembler.Assembler.init_assembler`.

        :param config: the configuration data
        :type config: :class:`surround.config.Config`
        """

        if not config or not isinstance(config, Config):
            raise TypeError("config should be of class Config")
        self.config = config

        return self

    def set_stages(self, stages):
        """
        Set the stages to be executed one after the other in the pipeline.

        :param stages: list of stages to execute
        :type stages: list of :class:`surround.stage.Stage`
        """

        if not isinstance(stages, list) or not all([issubclass(type(x), Stage) for x in stages]):
            raise ValueError("stages must be a list of Stages's only!")

        self.stages = stages

        return self

    def set_finaliser(self, finaliser):
        """
        Set the final stage that will be executed no matter how the pipeline runs.
        This will be executed even when the pipeline fails or throws an error.

        :param finaliser: the final stage instance
        :type finaliser: :class:`surround.stage.Filter`
        """

        # finaliser must be a type of filter
        if not finaliser and not isinstance(finaliser, Filter):
            raise TypeError("finaliser should be of class Filter")
        self.finaliser = finaliser

        return self
