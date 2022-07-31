import sys
import sst

from morriganutils import mk, mklink

# One core, 2GHz, Ariel
# L1, 64KiB, MemH
# L2, 8MiB, MemH
# HBM Memory, 8GiB, 256 GB/s, DRAMSim3

freq             = "2.0GHz"
cache_line_bytes = "256"
coherence        = "MESI"
replacement      = "lru"
#exe              = "/home/plavin3/modsim22/AMG-master/test/amg"
exe = "/bin/ls"
latency          = "1000ps"

def arielParams(args):
      params   = {
            "verbose"        : 0,
            "corecount"      : 0,
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
            params["apparg" + str(i)] = args[i]

      return params


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

core    = mk(sst.Component("Ariel", "ariel.ariel"), arielParams([]))
l1      = mk(sst.Component("L1Cache", "memHierarchy.Cache"), l1Params)
l2      = mk(sst.Component("L2Cache", "memHierarchy.Cache"), l2Params)
memctrl = mk(sst.Component("MemoryController", "memHierarchy.MemController"), memctrlParams)
mem     = mk(memctrl.setSubComponent("backend", "memHierarchy.dramsim3"), dramsim3Params)

mklink((core, "cache_link_0", latency),
       (l1,   "high_network_0", latency))

mklink((l1, "low_network_0", latency),
       (l2, "high_network_0", latency))

mklink((l2, "low_network_0", latency),
       (memctrl, "direct_link", latency))


