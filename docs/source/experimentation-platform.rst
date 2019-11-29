Experimentation
===============

Surround's Experimentation Platform records experiments executed from anywhere (local or cloud).
Recording all artifacts from the experiment including:

- Source code
- Configuration data
- Model (if any used)
- Output
- Experiment Report (metrics and/or visualisations)

Each time an experiment is executed, the above artifacts are transferred to
a separate storage location.

**Supported Storage Locations**:

- File System (local)
- Google Cloud Storage Bucket (cloud)

Configure
#########

Setup user information
^^^^^^^^^^^^^^^^^^^^^^
Surround needs to know your name and email before you can start creating experiments. This is
so then you can differentiate between who created what experiment, especially when sharing
an experiment storage location with multiple users.

Use the following commands to setup your name and email::

    $ surround config user.name "John Doe"
    $ surround config user.email "john.doe@email.com"

Use File System for Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default, Surround uses the path ``~/.experiments/local`` for experiment storage.

If you would like to use another path, then you can use the following command::

    $ surround config experiment.url /path/to/experiment/storage

Use Google Cloud Bucket for Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Surround also supports using Google Cloud storage buckets for experiment storage.
This is especially useful for sharing an experiment location with multiple users.

Setup Google Cloud credentials
******************************
You will need to login to the `Google Cloud Platform Console <https://console.cloud.google.com>`_ (create an account if you don't have one). 

Once logged in, follow this guide to help you create a project:
`GCP Create Project Guide <https://cloud.google.com/resource-manager/docs/creating-managing-projects>`_.

Next you will need a Service Account, this is how Surround will be authorized to access your bucket:

1. In the GCP Console, navigate to **Storage Accounts** --> **IAM & admin**
2. Select **+ CREATE SERVICE ACCOUNT**
3. Give the service account a name e.g. ``surround-access``
4. Select **CREATE**
5. Under **Service Account Permissions**   

   a. Give the account the role **Storage Object Admin**
   b. Give the account the role **ML Engine Developer** (so it can deploy training compute jobs)

6. Select **DONE**

Next you will need to create keys that can be used by Surround:

1. In the Google Cloud Console, navigate to **IAM & admin** → **Service Accounts**
2. Select the Service Account you created in the previous section
3. Select **EDIT** then select **+ CREATE KEY**
4. Select **JSON** as the key type
5. Select **CREATE** and then a JSON document with your keys will be downloaded
6. Store this file somewhere secret (just not easily accessible)

Lastly, you need to set the environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to the path
where your credentials JSON file is located:

**MacOS** / **Linux**:

Put the following in ``~/.bashrc`` and/or ``~/.bash_profile``::

    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials

**Windows**:

Run the following in Command Prompt or PowerShell::

    SETX GOOGLE_APPLICATION_CREDENTIALS C:\path\to\credentials

Configure Surround to use the bucket
************************************
Now we just need to tell Surround to look for the bucket when writing experiments::

    $ surround config experiment.url gs://bucket-name-here

After running this command, when experiments are ran their artifacts will be transferred to
the bucket specified.

Usage
#####

Run experiments
^^^^^^^^^^^^^^^
By default in the generated project, any time you run the project it is considered an experiment.
So to run an experiment, just simply create a project and run a batch job::

    $ surround run batch

Or a training job::

    $ surround run train

.. note:: To disable the experiment platform for a single run, use the ``--no-experiment`` flag!

.. warning:: If you run the job in the cloud, then the experimentation platform will only work
        when using a bucket for experiment storage! 

.. warning:: If you are on Windows and are running the job in a container (``train`` or ``batch``), ensure your project
        is located in a directory Docker can mount to (typically anywhere in the user directory e.g. Documents)

View projects & experiments
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The experimentation platform also comes with a web application which can manage/view experiments
stored in the experiment storage location.

To start this web app, use the following command::

    $ surround experimentation
    INFO:surround.experiment.web.cli:Starting the experimentation platform server...
    INFO:surround.experiment.web.cli:Server started at: http://localhost:45710

This will automatically bring up your default browser, showing all projects available in storage:

.. image:: project_explorer.png
    :alt: Experimentation Web App
    :align: center

When you select a project, it will bring up the Experiment Explorer, showing all past experiments:

.. image:: experiment_explorer.png
    :alt: Experimentation Web App
    :align: center

Where you can view result reports, view logs, view/edit notes, download and delete experiments.

Here is an example of how the log view looks:

.. image:: view_logs.png
    :alt: Experimentation Web App
    :align: center

Here is an example of what an experiment report can look like:

.. image:: experiment_report.png
    :alt: Experimentation Web App
    :align: center

Set metrics during the experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When you generate a project, you are given a file called ``assembler_state.py`` which contains
the class ``AssemblerState``. This class is used to store information between stages in the pipeline.

This typically looks like so::

    class AssemblerState(State):
        def __init__(self, input_data):
            super().__init__()
            self.input_data = input_data
            self.output_data = None
            self.metrics = {}

To add metrics that can then be viewed later in the Experiment Report, just add them to the
state's ``metrics`` dictionary, like so::

    class Baseline(Estimator):
        def estimate(self, state, config):
            state.metrics['accuracy_score'] = self.calc_accuracy()

The ``ReportGenerator`` stage will handle gathering the metrics and displaying them in a HTML report.

Modify the Experiment Report
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default the ``ReportGenerator`` class, which comes with all generated projects, will generate
a HTML report based on the template located in the templates folder ``templates/report.html``.

In this template, it shows two tables, one showing all of the metrics recorded in the ``AssemblerState`` object
during the experiment, another showing the all of the configuration values that were set for
the experiment.

The template is rendered using `Tornado <https://www.tornadoweb.org/en/stable/template.html>`_'s template
system.

Render an image in the report
*****************************
For exmaple to render an image in the template, you will need to do the following:

#. During the pipeline somewhere render a PNG or JPEG image and convert it to base64::

    import base64
    with open("image.png", "rb") as f:
        state.image = f.read()
        state.image = base64.b64encode(image)
        state.image = image.encode('utf-8)

#. Then construct a Data URI, replacing ``image/png`` with the mime type of your image (more info `here <https://css-tricks.com/data-uris/>`_)::

    state.image = "data:image/png;base64,%s" % state.image

#. Now in the template file (``templates/report.html``) you will need to add an ``img`` tag with the ``src`` attribute set to the data URI from the state object::

    <img src="{{state.image}}" width=100 height=50 />

#. Then run an experiment, you should see the image in the report generated in the output folder (You can also see the report in the Experiment Explorer by clicking on the experiment's timestamp.)