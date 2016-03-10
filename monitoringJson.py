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
systemMonitoringJson = {}

# Calling the monit status command using the Popen sub-module of subprocess.
monitProcess = subprocess.Popen(['monit', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Output contains the monit status command.
output, error = monitProcess.communicate()


processLineRegex = re.findall(r'Process\s.*', output)
processExtractArray = [];
for process in processLineRegex:
    intermediate = (re.sub('Process \'', '', process))
    processExtractArray.append(re.sub('\'', '', intermediate))

print processExtractArray




# The output looks like this. Now need to extract the needed value using regular expression.

# System ''
#  status                            Running
#  monitoring status                 Monitored
#  load average                      [0.07] [0.18] [0.18]
#  cpu                               0.0%us 0.1%sy
#  memory usage                      70.3 MB [14.4%]
#  swap usage                        0 B [0.0%]
#  data collected                    Sun, 06 Mar 2016 05:56:10

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

# Encoding as a json using the json module.
systemMonitoringJsonEncoding = json.dumps(systemMonitoringJson)

# Printing the systemMonitoringJson.
print systemMonitoringJsonEncoding
