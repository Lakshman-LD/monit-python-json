# 1. Script prints a human readable and understandable json from the output of monit status command.
# 2. The file can be called from any backend services for a periodic time intervals to get this
# monitoring data in the form of an json.
# 3. Easy for the backed sevices to get the monitoring details of the server and take necessary steps accordingly.

# subprocees is the module for executing shell commands from python.
import subprocess
# re is the regular expression module.
import re
# json for performing the json encoding.
import json

# Initialising the json.
monitoringJson = {}
systemMonitoringJson = {}

# Calling the monit status command using the Popen sub-module of subprocess.
monitProcess = subprocess.Popen(['monit', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Output contains the monit status command.
output, error = monitProcess.communicate()


# The output looks like this. Now need to extract the needed value using regular expression.

    # Process 'nginx'
    #  status                            Running
    #  monitoring status                 Monitored
    #  pid                               1033
    #  parent pid                        1
    #  uid                               0
    #  effective uid                     0
    #  gid                               0
    #  uptime                            1h 4m
    #  children                          1
    #  memory                            5.5 MB
    #  memory total                      11.3 MB
    #  memory percent                    1.1%
    #  memory percent total              2.3%
    #  cpu percent                       0.0%
    #  cpu percent total                 0.0%
    #  data collected                    Thu, 10 Mar 2016 12:14:24

    # System ''
    #  status                            Running
    #  monitoring status                 Monitored
    #  load average                      [0.07] [0.18] [0.18]
    #  cpu                               0.0%us 0.1%sy
    #  memory usage                      70.3 MB [14.4%]
    #  swap usage                        0 B [0.0%]
    #  data collected                    Sun, 06 Mar 2016 05:56:10


# Extracting the process name
processLineRegex = re.findall(r'Process\s.*', output)
processExtractArray = [];
for process in processLineRegex:
    intermediate = (re.sub('Process \'', '', process))
    processExtractArray.append(re.sub('\'', '', intermediate))

# Extracting the status of the service
statusLineRegex = re.findall(r'Process\s.*\n\s*status.*', output)
statusExtractArray = [];
for status in statusLineRegex:
    statusExtractArray.append(re.sub(r'Process\s.*\n\s*status\s*', '', status))

# Extracting the pid of the service
pidLineRegex = re.findall(r'\n\s*pid.*', output)
pidExtractArray = []
for pid in pidLineRegex:
    pidExtractArray.append(re.sub(r'\D', '', pid))

# Extracting the memory of the service
memoryTotalLineRegex = re.findall(r'memory\stotal.*', output)
memoryTotalExtractArray = []
for mt in memoryTotalLineRegex:
    memoryTotalExtractArray.append(re.sub(r'memory\stotal\s*', '', mt))

# Extracting the memory percentage of the service
memoryPercentTotalLineRegex = re.findall(r'memory\spercent\stotal.*', output)
memoryPercentTotalExtractArray = []
for mpt in memoryPercentTotalLineRegex:
    intermediate = re.sub(r'memory\spercent\stotal\s*', '', mpt)
    memoryPercentTotalExtractArray.append(re.sub(r'%', '', intermediate))

# Extracting the cpu percentage of the service
cpuPercentTotalLineRegex = re.findall(r'cpu\spercent\stotal.*', output)
cpuPercentTotalExtractArray = []
for cpt in cpuPercentTotalLineRegex:
    intermediate = re.sub(r'cpu\spercent\stotal\s*', '', cpt)
    cpuPercentTotalExtractArray.append(re.sub(r'%', '', intermediate))

# creating the json
monitoringJson['message'] = {}
for service in range(0, len(processExtractArray)):
    processJson = {}
    processJson['status'] = statusExtractArray[service]
    processJson['pid'] = pidExtractArray[service]
    processJson['memoryTotal'] = memoryTotalExtractArray[service]
    processJson['memoryPercent'] = memoryPercentTotalExtractArray[service]
    processJson['cpuPercent'] = cpuPercentTotalExtractArray[service]
    monitoringJson['message'][processExtractArray[service]] = processJson

# For system monitaring details.
# Extracting the load average.
# LoadAverage is used to find the idle state, no. of processes waiting for the resources.
# LoadAverage is generaaly given by the uptime command.
# LoadAverage gives a three values namely the loadAverage taken at 1, ,5 and 15 minute time intervals.

loadAverageLineRegex = re.search(r'load\s.*', output)

loadAverageRegex = re.search(r'\[\d.\d*\].*', loadAverageLineRegex.group())
loadAverageExtractArray = loadAverageRegex.group().split(' ')


loadAverageArray = [];
for la in loadAverageExtractArray:
    removedOpenBraces = re.sub('\[', '', la)
    loadAverageArray.append(re.sub('\]', '', removedOpenBraces))

la1 = loadAverageArray[0]
la5 = loadAverageArray[1]
la15 = loadAverageArray[2]

# Storing the loadAverage at 1, 5 and 15 minute intervals.
systemMonitoringJson['loadAverage1'] = la1
systemMonitoringJson['loadAverage5'] = la5
systemMonitoringJson['loadAverage15'] = la15

# CpuUserSpace is the amount of cpu used by the user. i.e the user space(user processes).
cpuUserSpaceRegex = re.search(r'\d*.\d\%us', output)
cpuUserSpaceExtract = cpuUserSpaceRegex.group()
cpuUserSpace = re.sub('%us','',cpuUserSpaceExtract)

# Storing the cpuUserSpace in json.
systemMonitoringJson['cpuUserSpace'] = cpuUserSpace

# CpuKernelSpace is the amount of cpu used by the system. i.e the kernel space(system processes).
cpuKernelSpaceRegex = re.search(r'\d*.\d\%sy', output)
cpuKernelSpaceExtract = cpuKernelSpaceRegex.group()
cpuKernelSpace = re.sub('%sy','',cpuKernelSpaceExtract)

# Storing the cpuKernelSpace in json.
systemMonitoringJson['cpuKernelSpace'] = cpuKernelSpace

# Memory usage of the system is represented both in value and in percentage.
# Memory usually denotes the ram.
memoryUsageLineRegex = re.search(r'memory\susage.*', output)

memoryUsageValueRegex = re.search(r'\d*.\d\s\w*\s', memoryUsageLineRegex.group())
memoryUsageValue =  memoryUsageValueRegex.group()

# Storing the memoryUsageValue in json.
systemMonitoringJson['memoryUsageValue'] = memoryUsageValue

memoryUsagePercentageRegex = re.search(r'\[.*', memoryUsageLineRegex.group())
memoryUsagePercentageExtract =  memoryUsagePercentageRegex.group()
removedOpenBracesMUP = re.sub('\[', '', memoryUsagePercentageExtract)
memoryUsagePercentage = re.sub('\]', '', removedOpenBracesMUP)

# Storing the memoryUsagePercentage in json.
systemMonitoringJson['memoryUsagePercentage'] = memoryUsagePercentage

# Swap usage is the additional memory needed in addition to the physical ram.
# Usually when the swap space increase, it is an indication that ram is filled and
# lot of paging has been occurred.
# Swap usage is aldo represented in both the value and in percentage.
swapUsageLineRegex = re.search(r'swap\s.*', output)

swapUsageValueRegex = re.search(r'\d*.\d\s\w*\s', swapUsageLineRegex.group())
swapUsageValue =  swapUsageValueRegex.group()

# Storing the swapUsageValue in json.
systemMonitoringJson['swapUsageValue'] = swapUsageValue

swapUsagePercentageRegex = re.search(r'\[.*', swapUsageLineRegex.group())
swapUsagePercentageExtract =  swapUsagePercentageRegex.group()
removedOpenBracesSUP = re.sub('\[', '', swapUsagePercentageExtract)
swapUsagePercentage = re.sub('\]', '', removedOpenBracesSUP)

# Storing the swapUsagePercentage in json.
systemMonitoringJson['swapUsagePercentage'] = swapUsagePercentage

monitoringJson['message']['system'] = systemMonitoringJson

# Encoding as a json using the json module.
monitoringJsonEncoding = json.dumps(monitoringJson)

# Printing the systemMonitoringJson.
print monitoringJsonEncoding
