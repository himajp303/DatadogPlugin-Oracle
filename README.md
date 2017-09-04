# DatadogPlugin-Oracle
This is the updated version of datadog oracle plugin (https://github.com/DataDog/integrations-extras/tree/contributor/oracle/oracle) with dsn connectivity error fixes


Installation steps

1) Copy the oracle.py into /etc/dd-agent/checks.d/​ keep the same name "oracle" for both the py & yaml file

2) Copy the oracle.yaml into /etc/dd-agent/conf.d/ change the server details with yours & perform the below steps

# The Oracle check requires access to the `cx_Oracle` Python
  # module. Due to restrictions on installation, this requires
  # the following steps in order to be included with the agent
  #
  # 1. Download the relevant Oracle Instant Client:
  #    http://www.oracle.com/technetwork/database/features/instant-client/index-097480.html
  #    Both the basic client and the client sdk will be required
  #    Example dir: ~/oracle
  # 2. Decompress this library in a given directory available to
  #    all users on the given machine (i.e. /opt/oracle)
  #       mkdir -p /opt/oracle/ && cd /opt/oracle/
  #       unzip ~/oracle/instantclient-basic-linux.x64-12.1.0.2.0.zip
  #       unzip ~/oracle/instantclient-sdk-linux.x64-12.1.0.2.0.zip
  # 3. Set required env variables for cx_Oracle installation
  #       export LD_RUN_PATH=/opt/oracle/instantclient_12_1
  #       export ORACLE_HOME=/opt/oracle/instantclient_12_1
  # 4. Install instant client in agent's virtual environment
  #       /opt/datadog-agent/embedded/bin/pip install cx_Oracle
  # 5. Following cx_Oracle installation, ensure LD_LIBRARY_PATH points
  #    to this directory when starting/restarting the agent
  #       export LD_LIBRARY_PATH=/opt/oracle/instantclient_12_1

3) Restart the agent
