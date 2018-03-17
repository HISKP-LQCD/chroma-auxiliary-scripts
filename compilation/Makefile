SHELL = /bin/bash

bootstrap-chroma: head.sh args.sh tail.sh
	cat $^ > $@
	chmod +x $@

args.sh: args.m4
	argbash $< --no-commented > args-raw.sh
	start_line=$$(grep -n 'START OF CODE' args-raw.sh | cut -d: -f1) && \
		   tail -n +$$start_line args-raw.sh > $@
