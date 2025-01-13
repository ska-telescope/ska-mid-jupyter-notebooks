.. skeleton documentation master file, created by
   sphinx-quickstart on Thu May 17 15:17:35 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SKA MID ITF Engineering tools
=============================

SKA MID ITF Engineering tools

.. toctree::
   :maxdepth: 2
   :caption: Readme

   README


README: Events and Logs Parser for Sequence Diagram Generation
=============================================================

The sequence_diagrams.ipynb notebook facilitates generating sequence diagrams from events and logs captured during testing of the **SUT (System Under Test)**. It uses device hierarchies and pod configurations to collect and process data, ultimately producing a **PlantUML sequence diagram**. Follow the steps outlined below to set up, execute, and generate the diagrams.

---

Workflow
--------

1. **Define Dish Indexes**:
   In the **tracked devices and pods setup**, specify the dish indexes to monitor (e.g., ``['001', '036']``).

2. **Setup Environment**:
   - Import required modules, configure global settings, and define Tango devices, namespaces, and pods for the SUT and Dish devices.
   - Device hierarchies are used to map relationships between components, aiding in identifying "likely callers" during event parsing.

3. **Start Event Monitoring**:
   - Instantiate the ``EventPrinter`` class to monitor attribute changes for tracked devices.
   - Start the event printer before running tests on your SUT or other devices.

4. **Run Test Scenarios**:
   Execute your desired test cases or commands on the SUT using separate scripts or notebooks.

5. **Stop Event Monitoring**:
   Exit the event printer to unsubscribe from all attributes.

6. **Retrieve Logs**:
   Use ``kubectl`` commands to collect logs from defined pods across namespaces. The logs are adjusted for time differences and stored locally.

7. **Parse Events and Logs**:
   Combine captured events and logs into a unified, sorted file for further processing.

8. **Generate Sequence Diagram**:
   Use the ``EventsAndLogsFileParser`` class to parse the combined file and generate a **PlantUML sequence diagram**.

---

Optional Flags in the Parser
----------------------------

The ``EventsAndLogsFileParser`` provides the following options to customize diagram generation:

+-----------------------------------+---------------+-------------------------------------------------------------------------------------+
| Flag                              | Default Value | Description                                                                         |
+===================================+===============+=====================================================================================+
| ``limit_track_load_table_calls``  | ``True``      | Limit the number of ``TrackLoadTable`` commands in the diagram to reduce verbosity. |
+-----------------------------------+---------------+-------------------------------------------------------------------------------------+
| ``show_events``                   | ``False``     | Include all events in the diagram for a detailed view of interactions.             |
+-----------------------------------+---------------+-------------------------------------------------------------------------------------+
| ``show_component_state_updates``  | ``False``     | Display component state updates as hexagonal notes in the sequence diagram.        |
+-----------------------------------+---------------+-------------------------------------------------------------------------------------+
| ``include_dividers``              | ``True``      | Add dividers to the diagram for better visual separation between commands.         |
+-----------------------------------+---------------+-------------------------------------------------------------------------------------+
| ``use_new_pages``                 | ``True``      | Split large diagrams into multiple pages when major notebook commands are executed.|
+-----------------------------------+---------------+-------------------------------------------------------------------------------------+
| ``group_devices``                 | ``True``      | Organize devices into color-coded boxes based on their group (e.g., TMC, CSP, SDP, Dishes). |
+-----------------------------------+---------------+-------------------------------------------------------------------------------------+

---

Generated Outputs
-----------------

- **Events and Logs File**:
  Combines and sorts events and logs into a single file: ``events_and_logs-<date>-<time>.txt``.

- **PlantUML Sequence Diagram**:
  A ``.puml`` file containing the sequence diagram code: ``sequence-diagram-<date>-<time>.puml``.
