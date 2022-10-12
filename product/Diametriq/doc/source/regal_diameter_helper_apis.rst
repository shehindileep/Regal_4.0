.. _regaldiameter:


**Regal Diameter Helper APIs**
=================================

Regal 4.0 Test Automation Framework provides python module with helper APIs for performing operations on the Diameter Stack. This custom python module is named as Diameter Helper module.
The Regal Diameter Helper Module comprises of a class with common helper tool functions shared between the products Diameter and Diametriq. This module also provides helper APIs for testing and benchmarking Diameter Performance. Below are the definitions of the class and the APIs that be used from this python module.

File path : regal_lib/product/Diametriq/helper/diameter_perf_tool_helper.py

Use the below line to import the DiameterPerfHelper
from Diametriq.helper.diameter_perf_tool_helper import DiameterPerfHelper

Object creation : diaperf_obj = DiameterPerfHelper(node_name, app_name, dia_type)

.. automodule:: diameter_perf_tool_helper
.. autoclass:: DiameterPerfHelper

   .. automethod:: setup_tool

      Snippet:

      .. literalinclude:: ../../regal_lib/product/Diametriq/helper/snippet.py
         :language: python
         :lines: 2

   .. automethod:: start_stats

      Snippet:

      .. literalinclude:: ../../regal_lib/product/Diametriq/helper/snippet.py
         :language: python
         :lines: 5

   .. automethod:: start_tool

      Snippet:

      .. literalinclude:: ../../regal_lib/product/Diametriq/helper/snippet.py
         :language: python
         :lines: 8

   .. automethod:: start_traffic

      Snippet:

      .. literalinclude:: ../../regal_lib/product/Diametriq/helper/snippet.py
         :language: python
         :lines: 11

   .. automethod:: stop_stats

      Snippet:

      .. literalinclude:: ../../regal_lib/product/Diametriq/helper/snippet.py
         :language: python
         :lines: 14

   .. automethod:: stop_tool

      Snippet:

      .. literalinclude:: ../../regal_lib/product/Diametriq/helper/snippet.py
         :language: python
         :lines: 17

   .. automethod:: stop_traffic

      Snippet:

      .. literalinclude:: ../../regal_lib/product/Diametriq/helper/snippet.py
         :language: python
         :lines: 20










Sample Usage
-----------------

.. code-block:: python

  import time
  from Diametriq.helper.diameter_perf_tool_helper import DiameterPerfHelper

  class RouteToDSS (object):
        """
        Initialize all the required parameter to start the test case.
        """
        def __init__(self):
                self._diaperf_obj = DiameterPerfHelper("pgw", "MME", "c")

        def _setup_diameter_app (self):
                """
                Method for Setup tool
                """
                self._diaperf_obj.setup_tool(mml=True)

        def _start_diameter_tool (self):
                """
                Method to start the tool
                """
                self._diaperf_obj.start_tool()

        def _start_diameter_traffic (self):
                """
                Method to start the traffic
                """
                self._diaperf_obj. start_traffic ()
                time.sleep(10)

        def _stop_diameter(self):
                """
                Method to cleanup and exit the test
                """
                self._diaperf_obj.stop_traffic()
                self._diaperf_obj.stop_tool()

        def exit_(self):
                """
                Stop all the services, tools and delete object created
                Returns:
                        None
                """
                self._diaperf_obj = None

        def test_run(self):
                """
                Method to start/stop the test case execution
                """
                try:
                        self._setup_diameter_app()
                        self._start_diameter_tool()
                        self._start_diameter_traffic()
                        time.sleep(self._test_run_duration)
                        self._stop_diameter()
                        self.exit_()

  def execute():
        """
        Execution of Test Case starts here
        """
        test = RouteToDSS()
        test.test_run()
        test = None

