SHELL = /bin/bash

bootstrap-chroma: head.sh args.sh tail.sh
	if [[ -f $@ ]]; then chmod u+w $@; fi
	cat $^ > $@
	chmod +x $@
	chmod -w $@

args.sh: args.m4
	if [[ -f $@ ]]; then chmod u+w $@; fi
	argbash $< --no-commented > args-raw.sh
	start_line=$$(grep -n 'START OF CODE' args-raw.sh | cut -d: -f1) && \
		   tail -n +$$start_line args-raw.sh > $@
	chmod -w $@
