#@ job_name = hmc-$(jobid)
#@ output = $(job_name)-out.txt
#@ error = $(job_name)-err.txt
#@ environment = COPY_ALL
#@ wall_clock_limit = 00:30:00
#@ notification = always
#@ notify_user = ueding@hiskp.uni-bonn.de
#@ job_type = bluegene
#@ bg_size = 32
#@ queue

runjob --ranks-per-node 1 --np 32 : \
    hmc -i testrun.ini.xml -o testrun.out.xml
