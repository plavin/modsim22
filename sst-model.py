import sys
import sst
from copy import copy

from morriganutils import mk, mklink

# One core, 2GHz, Ariel
# L1, 64KiB, MemH
# L2, 8MiB, MemH
# HBM Memory, 8GiB, 256 GB/s, DRAMSim3

freq             = "2.0GHz"
cache_line_bytes = "256"
coherence        = "MESI"
replacement      = "lru"
latency          = "1000ps"
#exe              = "/home/plavin3/modsim22/AMG-master/test/amg"
exe              = "/usr/bin/w"
args             = []

arielParams   = {
      "verbose"        : 1,
      "corecount"      : 1,
      "cachelinesize"  : cache_line_bytes,
      "executable"     : exe,
      "appargcount"    : len(args),
      "envparamcount"  : 1,
      "envparamname0"  : "OMP_NUM_THREADS",
      "envparamval0"   : 1,
      "clock"          : freq,
      "arielmode"      : 1,
}



for i in range(len(args)):
      arielParams["apparg" + str(i)] = args[i]

l1Params = {
      "cache_frequency"       : freq,
      "cache_size"            : "64KiB",
      "associativity"         : "4",
      "access_latency_cycles" : "2",
      "L1"                    : "1",
      "cache_line_size"       : cache_line_bytes,
      "coherence_protocol"    : coherence,
      "replacement_policy"    : replacement,
      #"prefetcher"            : "cassini.StridePrefetcher",
      "debug"                 : "0",
}

l2Params = {
      "access_latency_cycles" : "20",
      "cache_frequency"       : freq,
      "replacement_policy"    : replacement,
      "coherence_protocol"    : coherence,
      "associativity"         : "4",
      "cache_line_size"       : cache_line_bytes,
      #"prefetcher"            : "cassini.StridePrefetcher",
      "debug"                 : "0",
      "L1"                    : "0",
      "cache_size"            : "8MiB",
      "mshr_latency_cycles"   : "5",
}

memctrlParams = {
      "addr_range_start" : 0,
      "addr_range_end"   : 8*1024**3 - 1,
      "clock"   : freq,
      "backing" : "none",
}

dramsim3Params = {
      "config_ini"  : "/home/plavin3/morrigan/DRAMsim3/configs/HBM2_8Gb_x128.ini",
      "mem_size"    : "8GiB",
}

core    = mk(sst.Component("Ariel", "ariel.ariel"), arielParams)
l1      = mk(sst.Component("L1Cache", "memHierarchy.Cache"), l1Params)
l2      = mk(sst.Component("L2Cache", "memHierarchy.Cache"), l2Params)
memctrl = mk(sst.Component("MemoryController", "memHierarchy.MemController"), memctrlParams)

if (len(sys.argv) < 2):
      print("too few args")
      sys.exit(1)

if (sys.argv[1] == '-dramsim'):
      mem = mk(memctrl.setSubComponent("backend", "memHierarchy.dramsim3"), dramsim3Params)
elif (sys.argv[1] == '-simple'):
      mem = mk(memctrl.setSubComponent("backend", "memHierarchy.simpleMem"), {"mem_size" : "8GiB"})
else:
      print("Bad backend")
      sys.exit(1)
mklink((core, "cache_link_0", latency),
       (l1,   "high_network_0", latency))

mklink((l1, "low_network_0", latency),
       (l2, "high_network_0", latency))

mklink((l2, "low_network_0", latency),
       (memctrl, "direct_link", latency))

# Stats
#core.enableStatistics(["read_requests"])
#core.enableStatistics(["model_time"])
#core.enableAllStatistics({})
cacheStats = ["GetS_recv", "TotalEventsReceived", "GetSResp_recv"]
#l1.enableStatistics(copy(cacheStats))
#l2.enableStatistics(copy(cacheStats))



sst.setProgramOption("stopAtCycle", "200us")
#sst.setStatisticLoadLevel(10)
#sst.enableAllStatisticsForAllComponents()

sst.setStatisticOutput("sst.statOutputCSV", {"filepath": "stats.csv", "separator" : ", "} )


