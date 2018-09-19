# module: pyppl
  
!!! example "class: `PyPPL`"
  
	The PyPPL class  
  

	- **static variables:**  
		`TIPS`: The tips for users  
		`RUNNERS`: Registered runners  
		`DEFAULT_CFGFILES`: Default configuration file  
  
	!!! abstract "method: `__init__ (self, config, cfgfile)`"
  
		Constructor  

		- **params:**  
			`config`: the configurations for the pipeline, default: {}  
			`cfgfile`:  the configuration file for the pipeline, default: `~/.PyPPL.json` or `./.PyPPL`  
  
	!!! abstract "method: `flowchart (self, fcfile, dotfile)`"
  
		Generate graph in dot language and visualize it.  

		- **params:**  
			`dotfile`: Where to same the dot graph. Default: `None` (`path.splitext(sys.argv[0])[0] + ".pyppl.dot"`)  
			`fcfile`:  The flowchart file. Default: `None` (`path.splitext(sys.argv[0])[0] + ".pyppl.svg"`)  
			- For example: run `python pipeline.py` will save it to `pipeline.pyppl.svg`  
			`dot`:     The dot visulizer. Default: "dot -Tsvg {{dotfile}} > {{fcfile}}"  

		- **returns:**  
			The pipeline object itself.  
  
	!!! abstract "staticmethod: `registerRunner (runner)`"
  
		Register a runner  

		- **params:**  
			`runner`: The runner to be registered.  
  
	!!! abstract "method: `resume (self, *args)`"
  
		Mark processes as to be resumed  

		- **params:**  
			`args`: the processes to be marked  

		- **returns:**  
			The pipeline object itself.  
  
	!!! abstract "method: `resume2 (self, *args)`"
  
		Mark processes as to be resumed  

		- **params:**  
			`args`: the processes to be marked  

		- **returns:**  
			The pipeline object itself.  
  
	!!! abstract "method: `run (self, profile)`"
  
		Run the pipeline  

		- **params:**  
			`profile`: the profile used to run, if not found, it'll be used as runner name. default: 'default'  

		- **returns:**  
			The pipeline object itself.  
  
	!!! abstract "method: `showAllRoutes (self)`"
  
		Show all the routes in the log.  
  
	!!! abstract "method: `start (self, *args)`"
  
		Set the starting processes of the pipeline  

		- **params:**  
			`args`: the starting processes  

		- **returns:**  
			The pipeline object itself.  
  
!!! example "class: `Proc`"
  
	The Proc class defining a process  
  

	- **static variables:**  
		`RUNNERS`:       The regiested runners  
		`ALIAS`:         The alias for the properties  
		`LOG_NLINE`:     The limit of lines of logging information of same type of messages  
  

	- **magic methods:**  
		`__getattr__(self, name)`: get the value of a property in `self.props`  
		`__setattr__(self, name, value)`: set the value of a property in `self.config`  
  
	!!! abstract "method: `__getattr__ (self, name)`"
  
		Get the value of a property in `self.props`  
		It recognizes alias as well.  

		- **params:**  
			`name`: The name of the property  

		- **returns:**  
			The value of the property  
  
	!!! abstract "method: `__init__ (self, tag, desc, id, **kwargs)`"
  
		Constructor  

		- **params:**  
			`tag`:  The tag of the process  
			`desc`: The description of the process  
			`id`:   The identify of the process  

		- **config:**  
			id, input, output, ppldir, forks, cache, cclean, rc, echo, runner, script, depends, tag, desc, dirsig  
			exdir, exhow, exow, errhow, errntry, lang, beforeCmd, afterCmd, workdir, args, aggr  
			callfront, callback, expect, expart, template, tplenvs, resume, nthread  

		- **props**  
			input, output, rc, echo, script, depends, beforeCmd, afterCmd, workdir, expect  
			expart, template, channel, jobs, ncjobids, size, sets, procvars, suffix, logs  
  
	!!! abstract "method: `__setattr__ (self, name, value)`"
  
		Set the value of a property in `self.config`  

		- **params:**  
			`name` : The name of the property.  
			`value`: The new value of the property.  
  
	!!! abstract "method: `copy (self, tag, desc, id)`"
  
		Copy a process  

		- **params:**  
			`id`: The new id of the process, default: `None` (use the varname)  
			`tag`:   The tag of the new process, default: `None` (used the old one)  
			`desc`:  The desc of the new process, default: `None` (used the old one)  

		- **returns:**  
			The new process  
  
	!!! abstract "method: `log (self, msg, level, key)`"
  
		The log function with aggregation name, process id and tag integrated.  

		- **params:**  
			`msg`:   The message to log  
			`level`: The log level  
			`key`:   The type of messages  
  
	!!! abstract "method: `name (self, aggr)`"
  
		Get my name include `aggr`, `id`, `tag`  

		- **returns:**  
			the name  
  
	!!! abstract "method: `run (self, profile, profiles)`"
  
		Run the jobs with a configuration  

		- **params:**  
			`config`: The configuration  
  
# module: pyppl.aggr
  
The aggregation of procs  
  
!!! example "class: `Aggr`"
  
	The aggregation of a set of processes  
  
	!!! abstract "method: `__getattr__ (self, name)`"
  
		Get the property of an aggregation.  

		- **params:**  
			`name`: The name of the property  

		- **returns:**  
			- Return a proc if name in `self._procs`  
			- Return a property value if name in `self.__dict__`  
			- Return a `_Proxy` instance else.  
  
	!!! abstract "method: `__getitem__ (self, key)`"
  
		Select processes  
		```  
		# self._procs = OrderedDict([  
		#	('a', Proc(id = 'a')),  
		#	('b', Proc(id = 'b')),  
		#	('c', Proc(id = 'c')),  
		#	('d', Proc(id = 'd'))  
		# ])  
  
		self['a'] # proc a  
		self[0]   # proc a  
		self[1:2] # _Proxy of (proc b, proc c)  
		self[1,3] # _Proxy of (proc b, proc d)  
		self['b', 'c'] # _Proxy of (proc b, proc c)  
		self['b,c'] # _Proxy of (proc b, proc c)  
		self[Proc(id = 'd')] # proc d  
		```  
  
	!!! abstract "method: `__init__ (self, *args, **kwargs)`"
  
		Constructor  

		- **params:**  
			`args`: the set of processes  
			`depends`: Whether auto deduce depends. Default: True  
			`id`: The id of the aggr. Default: None (the variable name)  
			`tag`: The tag of the processes. Default: None (a unique 4-char str according to the id)  
  
	!!! abstract "method: `__setattr__ (self, name, value)`"
  
		Set property value of an aggregation.  
			- if it's a common property, set it to all processes  
			- if it is `input` set it to starting processes  
			- if it is `depends` set it to the end processes  
			- if it is related to `export` (startswith `ex`), set it to the end processes  
			- if it is in ['starts', 'ends', 'id'], set it to the aggregation itself.  
			- Otherwise a `ValueError` raised.  
			- You can use `[aggr].[proc].[prop]` to set/get the properties of a processes in the aggregation.  

		- **params:**  
			`name` : The name of the property  
			`value`: The value of the property  
  
	!!! abstract "method: `addEnd (self, *procs)`"
  
		Add end processes  

		- **params:**  
			`procs`: The selector of processes to add  
  
	!!! abstract "method: `addProc (self, p, tag, where, copy)`"
  
		Add a process to the aggregation.  
		Note that you have to adjust the dependencies after you add processes.  

		- **params:**  
			`p`:     The process  
			`where`: Add to where: 'starts', 'ends', 'both' or None (default)  

		- **returns:**  
			the aggregation itself  
  
	!!! abstract "method: `addStart (self, *procs)`"
  
		Add start processes  

		- **params:**  
			`procs`: The selector of processes to add  
  
	!!! abstract "method: `copy (self, tag, depends, id, delegates, modules)`"
  
		Like `proc`'s `copy` function, copy an aggregation. Each processes will be copied.  

		- **params:**  
			`tag`:      The new tag of all copied processes  
			`depends`: Whether to copy the dependencies or not. Default: True  
			- dependences for processes in starts will not be copied  
			`id`:    Use a different id if you don't want to use the variant name  
			`delegates`: Copy delegates? Default: `True`  
			`configs`: Copy configs? Default: `True`  

		- **returns:**  
			The new aggregation  
  
	!!! abstract "method: `delEnd (self, *procs)`"
  
		Delete end processes  

		- **params:**  
			`procs`: The selector of processes to delete  
  
	!!! abstract "method: `delStart (self, *procs)`"
  
		Delete start processes  

		- **params:**  
			`procs`: The selector of processes to delete  
  
	!!! abstract "method: `delegate (self, attrs, procs)`"
  
		Delegate the procs to have the attributes set by:  
		`aggr.args.a.b = 1`  
		Instead of setting `args.a.b` of all processes, `args.a.b` of only delegated processes will be set.  
		`procs` can be `starts`/`ends`, but it cannot be set with other procs, which means you can do:  
		`aggr.delegate('args', 'starts')`, but not `aggr.delegate('args', ['starts', 'pXXX'])`  
  
	!!! abstract "method: `module (self, name, starts, depends, ends, starts_shared, depends_shared, ends_shared)`"
  
		Define a function for aggr.  
		The "shared" parameters will be indicators not to remove those processes  
		when the shared function is on.  

		- **params:**  
			`name`          : The name of the function  
			`starts`        : A list of start processes.  
			`depends`       : A dict of dependences of the procs  
			`ends`          : A list of end processes  
			`starts_shared` : A dict of functions that shares the same starts  
			`depends_shared`: A dict of functions that shares the same depends  
			`ends_shared`   : A dict of functions that shares the same ends  
				- For example: `{<procs>: <func>}`  
  
	!!! abstract "method: `moduleFunc (self, name, on, off)`"
  
		Define modules using functions  

		- **params:**  
			`name`: The name of the module  
			`on`  : The function when the module is turned on  
			`off` : The function when the module is turned off  
  
	!!! abstract "method: `off (self, *names)`"
  
		Turn off modules  

		- **params:**  
			`names`: The names of the modules.  
  
	!!! abstract "method: `on (self, *names)`"
  
		Turn on modules  

		- **params:**  
			`names`: The names of the modules.  
  
# module: pyppl.channel
  
Channel for pyppl  
  
!!! example "class: `Channel`"
  
	The channen class, extended from `list`  
  
	!!! abstract "method: `attach (self, *names, **kwargs)`"
  
		Attach columns to names of Channel, so we can access each column by:  
		`ch.col0` == ch.colAt(0)  

		- **params:**  
			`names`: The names. Have to be as length as channel's width. None of them should be Channel's property name  
			`flatten`: Whether flatten the channel for the name being attached  
  
	!!! abstract "method: `cbind (self, *cols)`"
  
		Add columns to the channel  

		- **params:**  
			`cols`: The columns  

		- **returns:**  
			The channel with the columns inserted.  
  
	!!! abstract "method: `colAt (self, index)`"
  
		Fetch one column of a Channel  

		- **params:**  
			`index`: which column to fetch  

		- **returns:**  
			The Channel with that column  
  
	!!! abstract "method: `collapse (self, col)`"
  
		Do the reverse of expand  
		length: N -> 1  
		width:  M -> M  

		- **params:**  
			`col`:     the index of the column used to collapse  

		- **returns:**  
			The collapsed Channel  
  
	!!! abstract "method: `copy (self)`"
  
		Copy a Channel using `copy.copy`  

		- **returns:**  
			The copied Channel  
  
	!!! abstract "staticmethod: `create (l)`"
  
		Create a Channel from a list  

		- **params:**  
			`l`: The list, default: []  

		- **returns:**  
			The Channel created from the list  
  
	!!! abstract "method: `expand (self, col, pattern, t, sortby, reverse)`"
  
		expand the Channel according to the files in <col>, other cols will keep the same  
		`[(dir1/dir2, 1)].expand (0, "*")` will expand to  
		`[(dir1/dir2/file1, 1), (dir1/dir2/file2, 1), ...]`  
		length: 1 -> N  
		width:  M -> M  

		- **params:**  
			`col`:     the index of the column used to expand  
			`pattern`: use a pattern to filter the files/dirs, default: `*`  
			`t`:       the type of the files/dirs to include  
			  - 'dir', 'file', 'link' or 'any' (default)  
			`sortby`:  how the list is sorted  
			  - 'name' (default), 'mtime', 'size'  
			`reverse`: reverse sort. Default: False  

		- **returns:**  
			The expanded Channel  
  
	!!! abstract "method: `filter (self, func)`"
  
		Alias of python builtin `filter`  

		- **params:**  
			`func`: the function. Default: None  

		- **returns:**  
			The filtered Channel  
  
	!!! abstract "method: `filterCol (self, func, col)`"
  
		Just filter on the first column  

		- **params:**  
			`func`: the function  
			`col`: the column to filter  

		- **returns:**  
			The filtered Channel  
  
	!!! abstract "method: `flatten (self, col)`"
  
		Convert a single-column Channel to a list (remove the tuple signs)  
		`[(a,), (b,)]` to `[a, b]`  

		- **params:**  
			`col`: The column to flat. None for all columns (default)  

		- **returns:**  
			The list converted from the Channel.  
  
	!!! abstract "method: `fold (self, n)`"
  
		Fold a Channel. Make a row to n-length chunk rows  
		```  
		a1	a2	a3	a4  
		b1	b2	b3	b4  
		if n==2, fold(2) will change it to:  
		a1	a2  
		a3	a4  
		b1	b2  
		b3	b4  
		```  

		- **params:**  
			`n`: the size of the chunk  

		- **returns**  
			The new Channel  
  
	!!! abstract "staticmethod: `fromArgv ()`"
  
		Create a Channel from `sys.argv[1:]`  
		"python test.py a b c" creates a width=1 Channel  
		"python test.py a,1 b,2 c,3" creates a width=2 Channel  

		- **returns:**  
			The Channel created from the command line arguments  
  
	!!! abstract "staticmethod: `fromChannels (*args)`"
  
		Create a Channel from Channels  

		- **params:**  
			`args`: The Channels  

		- **returns:**  
			The Channel merged from other Channels  
  
	!!! abstract "staticmethod: `fromFile (fn, header, skip, delimit)`"
  
		Create Channel from the file content  
		It's like a matrix file, each row is a row for a Channel.  
		And each column is a column for a Channel.  

		- **params:**  
			`fn`:      the file  
			`header`:  Whether the file contains header. If True, will attach the header  
				- So you can use `channel.<header>` to fetch the column  
			`skip`:    first lines to skip  
			`delimit`: the delimit for columns  

		- **returns:**  
			A Channel created from the file  
  
	!!! abstract "staticmethod: `fromPairs (pattern)`"
  
		Create a width = 2 Channel from a pattern  

		- **params:**  
			`pattern`: the pattern  

		- **returns:**  
			The Channel create from every 2 files match the pattern  
  
	!!! abstract "staticmethod: `fromParams (*pnames)`"
  
		Create a Channel from params  

		- **params:**  
			`*pnames`: The names of the option  

		- **returns:**  
			The Channel  
  
	!!! abstract "staticmethod: `fromPattern (pattern, t, sortby, reverse)`"
  
		Create a Channel from a path pattern  

		- **params:**  
			`pattern`: the pattern with wild cards  
			`t`:       the type of the files/dirs to include  
			  - 'dir', 'file', 'link' or 'any' (default)  
			`sortby`:  how the list is sorted  
			  - 'name' (default), 'mtime', 'size'  
			`reverse`: reverse sort. Default: False  

		- **returns:**  
			The Channel created from the path  
  
	!!! abstract "method: `get (self, idx)`"
  
		Get the element of a flattened channel  

		- **params:**  
			`idx`: The index of the element to get. Default: 0  

		- **return:**  
			The element  
  
	!!! abstract "method: `insert (self, cidx, *cols)`"
  
		Insert columns to a channel  

		- **params:**  
			`cidx`: Insert into which index of column?  
			`cols`: the columns to be bound to Channel  

		- **returns:**  
			The combined Channel  
			Note, self is also changed  
  
	!!! abstract "method: `length (self)`"
  
		Get the length of a Channel  
		It's just an alias of `len(chan)`  

		- **returns:**  
			The length of the Channel  
  
	!!! abstract "method: `map (self, func)`"
  
		Alias of python builtin `map`  

		- **params:**  
			`func`: the function  

		- **returns:**  
			The transformed Channel  
  
	!!! abstract "method: `mapCol (self, func, col)`"
  
		Map for a column  

		- **params:**  
			`func`: the function  
			`col`: the index of the column. Default: 0  

		- **returns:**  
			The transformed Channel  
  
	!!! abstract "staticmethod: `nones (length, width)`"
  
		Create a channel with `None`s  

		- **params:**  
			`length`: The length of the channel  
			`width`:  The width of the channel  

		- **returns:**  
			The created channel  
  
	!!! abstract "method: `rbind (self, *rows)`"
  
		The multiple-argument versoin of `rbind`  

		- **params:**  
			`rows`: the rows to be bound to Channel  

		- **returns:**  
			The combined Channel  
			Note, self is also changed  
  
	!!! abstract "method: `reduce (self, func)`"
  
		Alias of python builtin `reduce`  

		- **params:**  
			`func`: the function  

		- **returns:**  
			The reduced value  
  
	!!! abstract "method: `reduceCol (self, func, col)`"
  
		Reduce a column  

		- **params:**  
			`func`: the function  
			`col`: the column to reduce  

		- **returns:**  
			The reduced value  
  
	!!! abstract "method: `repCol (self, n)`"
  
		Repeat column and return a new channel  

		- **params:**  
			`n`: how many times to repeat.  

		- **returns:**  
			The new channel with repeated columns  
  
	!!! abstract "method: `repRow (self, n)`"
  
		Repeat row and return a new channel  

		- **params:**  
			`n`: how many times to repeat.  

		- **returns:**  
			The new channel with repeated rows  
  
	!!! abstract "method: `rowAt (self, index)`"
  
		Fetch one row of a Channel  

		- **params:**  
			`index`: which row to fetch  

		- **returns:**  
			The Channel with that row  
  
	!!! abstract "method: `slice (self, start, length)`"
  
		Fetch some columns of a Channel  

		- **params:**  
			`start`:  from column to start  
			`length`: how many columns to fetch, default: None (from start to the end)  

		- **returns:**  
			The Channel with fetched columns  
  
	!!! abstract "method: `split (self, flatten)`"
  
		Split a Channel to single-column Channels  

		- **returns:**  
			The list of single-column Channels  
  
	!!! abstract "method: `t (self)`"
  
		Transpose the channel  

		- **returns:**  
			The transposed channel.  
  
	!!! abstract "method: `transpose (self)`"
  
		Transpose the channel  

		- **returns:**  
			The transposed channel.  
  
	!!! abstract "method: `unfold (self, n)`"
  
		Do the reverse thing as self.fold does  

		- **params:**  
			`n`: How many rows to combind each time. default: 2  

		- **returns:**  
			The unfolded Channel  
  
	!!! abstract "method: `unique (self)`"
  
		Make the channel unique, remove duplicated rows  
		Try to keep the order  
  
	!!! abstract "method: `width (self)`"
  
		Get the width of a Channel  

		- **returns:**  
			The width of the Channel  
  
# module: pyppl.flowchart
  
!!! example "class: `Flowchart`"
  
	Draw flowchart for pipelines  
  

	- **static variables:**  
		`THEMES`: predefined themes  
  
	!!! abstract "method: `__init__ (self, fcfile, dotfile)`"
  
		The constructor  

		- **params:**  
			`fcfile`: The flowchart file. Default: `path.splitext(sys.argv[0])[0] + '.pyppl.svg'`  
			`dotfile`: The dot file. Default: `path.splitext(sys.argv[0])[0] + '.pyppl.dot'`  
  
	!!! abstract "method: `addLink (self, node1, node2)`"
  
		Add a link to the chart  

		- **params:**  
			`node1`: The first node.  
			`node2`: The second node.  
  
	!!! abstract "method: `addNode (self, node, role)`"
  
		Add a node to the chart  

		- **params:**  
			`node`: The node  
			`role`: Is it a starting node, an ending node or None. Default: None.  
  
	!!! abstract "method: `generate (self)`"
  
		Generate the dot file and graph file.  
  
	!!! abstract "method: `setTheme (self, theme, base)`"
  
		Set the theme to be used  

		- **params:**  
			`theme`: The theme, could be the key of Flowchart.THEMES or a dict of a theme definition.  
			`base` : The base theme to be based on you pass custom theme  
  
# module: pyppl.job
  
Job module for pyppl  
  
!!! example "class: `Box`"
  
	Allow dot operation for OrderedDict  
  
	!!! abstract "method: `__getattr__ (self, name)`"
  
	!!! abstract "method: `__setattr__ (self, name, val)`"
  
	!!! abstract "method: `fromkeys (cls, iterable, value)`"
OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S.  
        If not specified, the value defaults to None.  
  
  
!!! example "class: `Job`"
  
	Job class, defining a job in a process  
  
	!!! abstract "method: `__init__ (self, index, proc)`"
  
		Constructor  

		- **params:**  
			`index`:   The index of the job in a process  
			`proc`:    The process  
  
	!!! abstract "method: `cache (self)`"
  
		Truly cache the job (by signature)  
  
	!!! abstract "method: `checkOutfiles (self, expect)`"
  
		Check whether output files are generated, if not, add - to rc.  
  
	!!! abstract "method: `done (self)`"
  
		Do some cleanup when job finished  
  
	!!! abstract "method: `export (self)`"
  
		Export the output files  
  
	!!! abstract "method: `init (self)`"
  
		Initiate a job, make directory and prepare input, output and script.  
  
	!!! abstract "method: `isExptCached (self)`"
  
		Prepare to use export files as cached information  
		True if succeed, otherwise False  
  
	!!! abstract "method: `isTrulyCached (self)`"
  
		Check whether a job is truly cached (by signature)  
  
	!!! abstract "method: `pid (self, val)`"
  
		Get/Set the job id (pid or the id from queue system)  

		- **params:**  
			`val`: The id to be set  
  
	!!! abstract "method: `rc (self, val)`"
  
		Get/Set the return code  

		- **params:**  
			`val`: The return code to be set. If it is None, return the return code. Default: `None`  
			If val == -1000: the return code will be negative of current one. 0 will be '-0'  

		- **returns:**  
			The return code if `val` is `None`  
			If rcfile does not exist or is empty, return 9999, otherwise return -rc  
			A negative rc (including -0) means output files not generated  
  
	!!! abstract "method: `report (self)`"
  
		Report the job information to logger  
  
	!!! abstract "method: `reset (self, retry)`"
  
		Clear the intermediate files and output files  
  
	!!! abstract "method: `signature (self)`"
  
		Calculate the signature of the job based on the input/output and the script  

		- **returns:**  
			The signature of the job  
  
	!!! abstract "method: `succeed (self)`"
  
		Tell if the job is successful by return code, and output file expectations.  

		- **returns:**  
			True if succeed else False  
  
# module: pyppl.jobmgr
  
!!! example "class: `Jobmgr`"
  
	Job Manager  
  
	!!! abstract "method: `__init__ (self, proc, runner)`"
  
		Job manager constructor  

		- **params:**  
			`proc`     : The process  
			`runner`   : The runner class  
  
	!!! abstract "method: `allJobsDone (self)`"
  
		Tell whether all jobs are done.  
		No need to lock as it only runs in one process (the watcher process)  

		- **returns:**  
			`True` if all jobs are done else `False`  
  
	!!! abstract "method: `canSubmit (self)`"
  
		Tell whether we can submit jobs.  

		- **returns:**  
			`True` if we can, otherwise `False`  
  
	!!! abstract "method: `halt (self, halt_anyway)`"
  
		Halt the pipeline if needed  
  
	!!! abstract "method: `progressbar (self, jid, loglevel)`"
  
		Generate progressbar.  

		- **params:**  
			`jid`: The job index.  
			`loglevel`: The log level in PyPPL log system  

		- **returns:**  
			The string representing the progressbar  
  
	!!! abstract "method: `run (self)`"
  
		Start to run the jobs  
  
	!!! abstract "method: `runPool (self, rq, sq)`"
  
		The pool to run jobs (wait jobs to be done)  

		- **params:**  
			`rq`: The run queue  
			`sq`: The submit queue  
  
	!!! abstract "method: `submitPool (self, sq)`"
  
		The pool to submit jobs  

		- **params:**  
			`sq`: The submit queue  
  
	!!! abstract "method: `watchPool (self, rq, sq)`"
  
		The watchdog, checking whether all jobs are done.  
  
# module: pyppl.logger
  
A customized logger for pyppl  
  
!!! example "class: `PyPPLLogFormatter`"
  
	logging formatter for pyppl  
  
	!!! abstract "method: `__init__ (self, fmt, theme, secondary)`"
  
		Constructor  

		- **params:**  
			`fmt`      : The format  
			`theme`    : The theme  
			`secondary`: Whether this is a secondary formatter or not (another formatter applied before this).  
  
	!!! abstract "method: `format (self, record)`"
  
		Format the record  

		- **params:**  
			`record`: The log record  

		- **returns:**  
			The formatted record  
  
!!! example "class: `PyPPLLogFilter`"
  
	logging filter by levels (flags)  
  
	!!! abstract "method: `__init__ (self, name, lvls, lvldiff)`"
  
		Constructor  

		- **params:**  
			`name`: The name of the logger  
			`lvls`: The levels of records to keep  
			`lvldiff`: The adjustments to `lvls`  
  
	!!! abstract "method: `filter (self, record)`"
  
		Filter the record  

		- **params:**  
			`record`: The record to be filtered  

		- **return:**  
			`True` if the record to be kept else `False`  
  
!!! example "class: `PyPPLStreamHandler`"
  
	PyPPL stream log handler.  
	To implement the progress bar for JOBONE and SUBMIT logs.  
  
	!!! abstract "method: `__init__ (self, stream)`"
  
		Constructor  

		- **params:**  
			`stream`: The stream  
  
	!!! abstract "method: `emit (self, record)`"
  
		Emit the record.  
  
!!! example "function: `getLogger`"
  
	Get the default logger  

	- **params:**  
		`levels`: The log levels(tags), default: basic  
		`theme`:  The theme of the logs on terminal. Default: True (default theme will be used)  
			- False to disable theme  
		`logfile`:The log file. Default: None (don't white to log file)  
		`lvldiff`:The diff levels for log  
			- ["-depends", "jobdone", "+debug"]: show jobdone, hide depends and debug  
		`name`:   The name of the logger, default: PyPPL  

	- **returns:**  
		The logger  
  
# module: pyppl.parameters
  
!!! example "class: `Parameters`"
  
	A set of parameters  
  
	!!! abstract "method: `__call__ (self, option, value)`"
  
		Set options values in `self._props`.  
		Will be deprecated in the future!  

		- **params:**  
			`option`: The key of the option  
			`value` : The value of the option  
			`excl`  : The value is used to exclude (only for `hopts`)  

		- **returns:**  
			`self`  
  
	!!! abstract "method: `__getattr__ (self, name)`"
  
	!!! abstract "method: `__getitem__ (self, name)`"
  
	!!! abstract "method: `__init__ (self, command, theme)`"
  
		Constructor  

		- **params:**  
			`command`: The sub-command  
			`theme`: The theme  
  
	!!! abstract "method: `__setattr__ (self, name, value)`"
  
	!!! abstract "method: `__setitem__ (self, name, value)`"
  
	!!! abstract "method: `asDict (self)`"
  
		Convert the parameters to Box object  

		- **returns:**  
			The Box object  
  
	!!! abstract "method: `help (self, error, printNexit)`"
  
		Calculate the help page  

		- **params:**  
			`error`: The error message to show before the help information. Default: `''`  
			`printNexit`: Print the help page and exit the program? Default: `False` (return the help information)  

		- **return:**  
			The help information  
  
	!!! abstract "method: `loadDict (self, dictVar, show)`"
  
		Load parameters from a dict  

		- **params:**  
			`dictVar`: The dict variable.  
			- Properties are set by "<param>.required", "<param>.show", ...  
			`show`:    Whether these parameters should be shown in help information  
				- Default: False (don't show parameter from config object in help page)  
				- It'll be overwritten by the `show` property inside dict variable.  
				- If it is None, will inherit the param's show value  
  
	!!! abstract "method: `loadFile (self, cfgfile, show)`"
  
		Load parameters from a json/config file  
		If the file name ends with '.json', `json.load` will be used,  
		otherwise, `ConfigParser` will be used.  
		For config file other than json, a section name is needed, whatever it is.  

		- **params:**  
			`cfgfile`: The config file  
			`show`:    Whether these parameters should be shown in help information  
				- Default: False (don't show parameter from config file in help page)  
				- It'll be overwritten by the `show` property inside the config file.  
  
	!!! abstract "method: `parse (self, args, arbi)`"
  
		Parse the arguments.  

		- **params:**  
			`args`: The arguments (list). `sys.argv[1:]` will be used if it is `None`.  
			`arbi`: Whether do an arbitrary parse. If True, options don't need to be defined. Default: `False`  

		- **returns:**  
			A `Box`/`dict` object containing all option names and values.  
  
!!! example "class: `Parameter`"
  
	The class for a single parameter  
  
	!!! abstract "method: `__getattr__ (self, name)`"
  
	!!! abstract "method: `__init__ (self, name, value)`"
  
		Constructor  

		- **params:**  
			`name`:  The name of the parameter  
			`value`: The initial value of the parameter  
  
	!!! abstract "method: `__setattr__ (self, name, value)`"
  
	!!! abstract "method: `setDesc (self, d)`"
  
		Set the description of the parameter  

		- **params:**  
			`d`: The description  
  
	!!! abstract "method: `setName (self, n)`"
  
		Set the name of the parameter  

		- **params:**  
			`n`: The name  
  
	!!! abstract "method: `setRequired (self, r)`"
  
		Set whether this parameter is required  

		- **params:**  
			`r`: True if required else False. Default: True  
  
	!!! abstract "method: `setShow (self, s)`"
  
		Set whether this parameter should be shown in help information  

		- **params:**  
			`s`: True if it shows else False. Default: True  
  
	!!! abstract "method: `setType (self, t)`"
  
		Set the type of the parameter  

		- **params:**  
			`t`: The type of the value. Default: str  
			- Note: str rather then 'str'  
  
	!!! abstract "method: `setValue (self, v)`"
  
		Set the value of the parameter  

		- **params:**  
			`v`: The value  
  
!!! example "class: `HelpAssembler`"
  
	A helper class to help assembling the help information page.  

	- **staticvars**  
		`MAXPAGEWIDTH`: the max width of the help page, not including the leading space  
		`MAXOPTWIDTH` : the max width of the option name (include the type and placeholder, but not the leading space)  
		`THEMES`      : the themes  
  
	!!! abstract "method: `__init__ (self, prog, theme)`"
  
		Constructor  

		- **params:**  
			`prog`: The program name  
			`theme`: The theme. Could be a name of `THEMES`, or a dict of a custom theme.  
  
	!!! abstract "method: `assemble (self, helps, progname)`"
  
		Assemble the whole help page.  

		- **params:**  
			`helps`: The help items. A list with plain strings or tuples of 3 elements, which  
				will be treated as option name, option type/placeholder and option descriptions.  
			`progname`: The program name used to replace '{prog}' with.  

		- **returns:**  
			lines (`list`) of the help information.  
  
	!!! abstract "method: `error (self, msg)`"
  
		Render an error message  

		- **params:**  
			`msg`: The error message  
  
	!!! abstract "method: `optdesc (self, msg)`"
  
		Render the option descriptions  

		- **params:**  
			`msg`: the option descriptions  
  
	!!! abstract "method: `optname (self, msg)`"
  
		Render the option name  

		- **params:**  
			`msg`: The option name  
  
	!!! abstract "method: `opttype (self, msg)`"
  
		Render the option type or placeholder  

		- **params:**  
			`msg`: the option type or placeholder  
  
	!!! abstract "method: `plain (self, msg)`"
  
		Render a plain message  

		- **params:**  
			`msg`: the message  
  
	!!! abstract "method: `prog (self, prog)`"
  
		Render the program name  

		- **params:**  
			`msg`: The program name  
  
	!!! abstract "method: `title (self, msg)`"
  
		Render an section title  

		- **params:**  
			`msg`: The section title  
  
	!!! abstract "method: `warning (self, msg)`"
  
		Render an warning message  

		- **params:**  
			`msg`: The warning message  
  
!!! example "class: `Commands`"
  
	Support sub-command for command line argument parse.  
  
	!!! abstract "method: `__getattr__ (self, name)`"
  
	!!! abstract "method: `__getitem__ (self, name)`"
  
	!!! abstract "method: `__init__ (self, theme)`"
  
		Constructor  

		- **params:**  
			`theme`: The theme  
  
	!!! abstract "method: `__setattr__ (self, name, value)`"
  
	!!! abstract "method: `help (self, error, printNexit)`"
  
		Construct the help page  

		- **params:**  
			`error`: the error message  
			`printNexit`: print the help page and exit instead of return the help information  

		- **returns:**  
			The help information if `printNexit` is `False`  
  
	!!! abstract "method: `parse (self, args, arbi)`"
  
		Parse the arguments.  

		- **params:**  
			`args`: The arguments (list). `sys.argv[1:]` will be used if it is `None`.  
			`arbi`: Whether do an arbitrary parse. If True, options don't need to be defined. Default: `False`  

		- **returns:**  
			A `tuple` with first element the subcommand and second the parameters being parsed.  
  
# module: pyppl.proctree
  
Manage process relations  
  
!!! example "class: `ProcNode`"
  
	The node for processes to manage relations between each other  
  
	!!! abstract "method: `__init__ (self, proc)`"
  
		Constructor  

		- **params:**  
			`proc`: The `Proc` instance  
  
	!!! abstract "method: `sameIdTag (self, proc)`"
  
		Check if the process has the same id and tag with me.  

		- **params:**  
			`proc`: The `Proc` instance  

		- **returns:**  
			`True` if it is.  
			`False` if not.  
  
# module: pyppl.runners.helpers
  
!!! example "class: `Helper`"
  
	A helper class for runners  
  
	!!! abstract "method: `__init__ (self, script, cmds)`"
  
		Constructor  

		- **params:**  
			`script`: The script of the job  
			`cmds`  : The original runner commands  
  
	!!! abstract "method: `alive (self)`"
  
		Tell if the job is alive  
  
	!!! abstract "method: `kill (self)`"
  
		Kill the job  
  
	!!! abstract "method: `run (self)`"
  
		Run the job, wait for the job to complete  
  
	!!! abstract "method: `submit (self)`"
  
		Submit the job  
  
# module: pyppl.runners.runner
  
The base runner class  
  
!!! example "class: `Runner`"
  
	The base runner class  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "method: `finish (self)`"
  
	!!! abstract "method: `getpid (self)`"
  
		Get the job id  
  
	!!! abstract "method: `isRunning (self)`"
  
		Try to tell whether the job is still running.  

		- **returns:**  
			`True` if yes, otherwise `False`  
  
	!!! abstract "method: `kill (self)`"
  
		Try to kill the running jobs if I am exiting  
  
	!!! abstract "method: `retry (self)`"
  
	!!! abstract "method: `run (self)`"
  

		- **returns:**  
			True: success/fail  
			False: needs retry  
  
	!!! abstract "method: `submit (self)`"
  
		Try to submit the job  
  
# module: pyppl.runners.runner_dry
  
Dry runner  
  
!!! example "class: `Runner`"
  
	The base runner class  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "method: `finish (self)`"
  
	!!! abstract "method: `getpid (self)`"
  
		Get the job id  
  
	!!! abstract "method: `isRunning (self)`"
  
		Try to tell whether the job is still running.  

		- **returns:**  
			`True` if yes, otherwise `False`  
  
	!!! abstract "method: `kill (self)`"
  
		Try to kill the running jobs if I am exiting  
  
	!!! abstract "method: `retry (self)`"
  
	!!! abstract "method: `run (self)`"
  

		- **returns:**  
			True: success/fail  
			False: needs retry  
  
	!!! abstract "method: `submit (self)`"
  
		Try to submit the job  
  
!!! example "class: `RunnerDry`"
  
	The dry runner  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "method: `finish (self)`"
  
		Do some cleanup work when jobs finish  
  
# module: pyppl.runners.runner_local
  
A runner wrapper for a single script  
Author: pwwang@pwwang.com  
Examples:  

	- **see runner.unittest.py**  
  
!!! example "class: `Runner`"
  
	The base runner class  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "method: `finish (self)`"
  
	!!! abstract "method: `getpid (self)`"
  
		Get the job id  
  
	!!! abstract "method: `isRunning (self)`"
  
		Try to tell whether the job is still running.  

		- **returns:**  
			`True` if yes, otherwise `False`  
  
	!!! abstract "method: `kill (self)`"
  
		Try to kill the running jobs if I am exiting  
  
	!!! abstract "method: `retry (self)`"
  
	!!! abstract "method: `run (self)`"
  

		- **returns:**  
			True: success/fail  
			False: needs retry  
  
	!!! abstract "method: `submit (self)`"
  
		Try to submit the job  
  
!!! example "class: `RunnerLocal`"
  
	Constructor  

	- **params:**  
		`job`:    The job object  
		`config`: The properties of the process  
  
	!!! abstract "method: `__init__ (self, job)`"
  
# module: pyppl.runners.runner_sge
  
!!! example "class: `Runner`"
  
	The base runner class  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "method: `finish (self)`"
  
	!!! abstract "method: `getpid (self)`"
  
		Get the job id  
  
	!!! abstract "method: `isRunning (self)`"
  
		Try to tell whether the job is still running.  

		- **returns:**  
			`True` if yes, otherwise `False`  
  
	!!! abstract "method: `kill (self)`"
  
		Try to kill the running jobs if I am exiting  
  
	!!! abstract "method: `retry (self)`"
  
	!!! abstract "method: `run (self)`"
  

		- **returns:**  
			True: success/fail  
			False: needs retry  
  
	!!! abstract "method: `submit (self)`"
  
		Try to submit the job  
  
!!! example "class: `RunnerSge`"
  
	The sge runner  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
			`config`: The properties of the process  
  
# module: pyppl.runners.runner_slurm
  
!!! example "class: `Runner`"
  
	The base runner class  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "method: `finish (self)`"
  
	!!! abstract "method: `getpid (self)`"
  
		Get the job id  
  
	!!! abstract "method: `isRunning (self)`"
  
		Try to tell whether the job is still running.  

		- **returns:**  
			`True` if yes, otherwise `False`  
  
	!!! abstract "method: `kill (self)`"
  
		Try to kill the running jobs if I am exiting  
  
	!!! abstract "method: `retry (self)`"
  
	!!! abstract "method: `run (self)`"
  

		- **returns:**  
			True: success/fail  
			False: needs retry  
  
	!!! abstract "method: `submit (self)`"
  
		Try to submit the job  
  
!!! example "class: `RunnerSlurm`"
  
	The slurm runner  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
			`config`: The properties of the process  
  
# module: pyppl.runners.runner_ssh
  
!!! example "class: `Runner`"
  
	The base runner class  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "method: `finish (self)`"
  
	!!! abstract "method: `getpid (self)`"
  
		Get the job id  
  
	!!! abstract "method: `isRunning (self)`"
  
		Try to tell whether the job is still running.  

		- **returns:**  
			`True` if yes, otherwise `False`  
  
	!!! abstract "method: `kill (self)`"
  
		Try to kill the running jobs if I am exiting  
  
	!!! abstract "method: `retry (self)`"
  
	!!! abstract "method: `run (self)`"
  

		- **returns:**  
			True: success/fail  
			False: needs retry  
  
	!!! abstract "method: `submit (self)`"
  
		Try to submit the job  
  
!!! example "class: `RunnerSsh`"
  
	The ssh runner  
  

	- **static variables:**  
		`SERVERID`: The incremental number used to calculate which server should be used.  
		- Don't touch unless you know what's going on!  
  
  
	!!! abstract "method: `__init__ (self, job)`"
  
		Constructor  

		- **params:**  
			`job`:    The job object  
  
	!!! abstract "staticmethod: `isServerAlive (server, key)`"
  
# module: pyppl.template
  
!!! example "class: `Template`"
  
	Template wrapper base  
  
	!!! abstract "method: `__init__ (self, source, **envs)`"
  
	!!! abstract "method: `registerEnvs (self, **envs)`"
  
	!!! abstract "method: `render (self, data)`"
  
!!! example "class: `TemplateJinja2`"
  
	Jinja2 template wrapper  
  
	!!! abstract "method: `__init__ (self, source, **envs)`"
  
		Initiate the engine with source and envs  

		- **params:**  
			`source`: The souce text  
			`envs`: The env data  
  
!!! example "class: `TemplateLiquid`"
  
	liquid.py template wrapper.  
  
	!!! abstract "method: `__init__ (self, source, **envs)`"
  
		Initiate the engine with source and envs  

		- **params:**  
			`source`: The souce text  
			`envs`: The env data  
  
# module: pyppl.utils
  
A set of utitities for PyPPL  
  
!!! example "function: `uid`"
  
	Calculate a short uid based on a string.  
	Safe enough, tested on 1000000 32-char strings, no repeated uid found.  
	This is used to calcuate a uid for a process  

	- **params:**  
		`s`: the base string  
		`l`: the length of the uid  
		`alphabet`: the charset used to generate the uid  

	- **returns:**  
		The uid  
  
!!! example "function: `reduce`"
  
	Python2 and Python3 compatible reduce  

	- **params:**  
		`func`: The reduce function  
		`vec`: The list to be reduced  

	- **returns:**  
		The reduced value  
  
!!! example "function: `funcsig`"
  
	Get the signature of a function  
	Try to get the source first, if failed, try to get its name, otherwise return None  

	- **params:**  
		`func`: The function  

	- **returns:**  
		The signature  
  
!!! example "function: `alwaysList`"
  
	Convert a string or a list with element  

	- **params:**  
		`data`: the data to be converted  

	- **examples:**  
		```python  
		data = ["a, b, c", "d"]  
		ret  = alwaysList (data)  
		# ret == ["a", "b", "c", "d"]  
		```  

	- **returns:**  
		The split list  
  
!!! example "function: `formatSecs`"
  
	Format a time duration  

	- **params:**  
		`seconds`: the time duration in seconds  

	- **returns:**  
		The formated string.  
		For example: "01:01:01.001" stands for 1 hour 1 min 1 sec and 1 minisec.  
  
!!! example "function: `split`"
  
	Split a string using a single-character delimter  

	- **params:**  
		`s`: the string  
		`delimter`: the single-character delimter  
		`trim`: whether to trim each part. Default: True  

	- **examples:**  
		```python  
		ret = split("'a,b',c", ",")  
		# ret == ["'a,b'", "c"]  
		# ',' inside quotes will be recognized.  
		```  

	- **returns:**  
		The list of substrings  
  
!!! example "function: `briefList`"
  
	Briefly show an integer list, combine the continuous numbers.  

	- **params:**  
		`l`: The list  

	- **returns:**  
		The string to show for the briefed list.  
  
!!! example "function: `map`"
  
	Python2 and Python3 compatible map  

	- **params:**  
		`func`: The map function  
		`vec`: The list to be maped  

	- **returns:**  
		The maped list  
  
!!! example "function: `varname`"
  
	Get the variable name for ini  

	- **params:**  
		`maxline`: The max number of lines to retrive. Default: 20  
		`incldot`: Whether include dot in the variable name. Default: False  

	- **returns:**  
		The variable name  
  
!!! example "function: `filter`"
  
	Python2 and Python3 compatible filter  

	- **params:**  
		`func`: The filter function  
		`vec`:  The list to be filtered  

	- **returns:**  
		The filtered list  
  
!!! example "function: `dictUpdate`"
  
	Update a dictionary recursively.  

	- **params:**  
		`origDict`: The original dictionary  
		`newDict`:  The new dictionary  

	- **examples:**  
		```python  
		od1 = {"a": {"b": {"c": 1, "d":1}}}  
		od2 = {key:value for key:value in od1.items()}  
		nd  = {"a": {"b": {"d": 2}}}  
		od1.update(nd)  
		# od1 == {"a": {"b": {"d": 2}}}, od1["a"]["b"] is lost  
		dictUpdate(od2, nd)  
		# od2 == {"a": {"b": {"c": 1, "d": 2}}}  
		```  
  
!!! example "function: `range`"
  
	Convert a range to list, because in python3, range is not a list  

	- **params:**  
		`r`: the range data  

	- **returns:**  
		The converted list  
  
!!! example "function: `asStr`"
  
	Convert everything (str, unicode, bytes) to str with python2, python3 compatiblity  
  
# module: pyppl.utils.box
  
!!! example "class: `Box`"
  
	Allow dot operation for OrderedDict  
  
	!!! abstract "method: `__getattr__ (self, name)`"
  
	!!! abstract "method: `__setattr__ (self, name, val)`"
  
	!!! abstract "method: `fromkeys (cls, iterable, value)`"
OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S.  
        If not specified, the value defaults to None.  
  
  
# module: pyppl.utils.cmd
  
!!! example "function: `run`"
  
	A shortcut of `Command.run`  
	To chain another command, you can do:  
	`run('seq 1 3', bg = True).pipe('grep 1')`  

	- **params:**  
		`cmd`     : The command, could be a string or a list  
		`bg`      : Run in background or not. Default: `False`  
			- If it is `True`, `rc` and `stdout/stderr` will be default (no value retrieved).  
		`raiseExc`: raise the expcetion or not  
		`**kwargs`: other arguments for `Popen`  

	- **returns:**  
		The `Command` instance  
  
!!! example "class: `Cmd`"
  
	A command (subprocess) wapper  
  
	!!! abstract "method: `__init__ (self, cmd, raiseExc, timeout, **kwargs)`"
  
		Constructor  

		- **params:**  
			`cmd`     : The command, could be a string or a list  
			`raiseExc`: raise the expcetion or not  
			`**kwargs`: other arguments for `Popen`  
  
	!!! abstract "method: `pipe (self, cmd, **kwargs)`"
  
		Pipe another command  

		- **examples:**  
			```python  
			c = Command('seq 1 3').pipe('grep 1').run()  
			c.stdout == '1\n'  
			```  

		- **params:**  
			`cmd`: The other command  
			`**kwargs`: Other arguments for `Popen` for the other command  

		- **returns:**  
			`Command` instance of the other command  
  
	!!! abstract "method: `run (self, bg)`"
  
		Wait for the command to run  

		- **params:**  
			`bg`: Run in background or not. Default: `False`  
				- If it is `True`, `rc` and `stdout/stderr` will be default (no value retrieved).  

		- **returns:**  
			`self`  
  
# module: pyppl.utils.parallel
  
!!! example "function: `run`"
  
	A shortcut of `Parallel.run`  

	- **params:**  
		`func`    : The function to run  
		`args`    : The arguments for the function, should be a `list` with `tuple`s  
		`nthread` : Number of jobs to run simultaneously. Default: `1`  
		`backend` : The backend, either `process` (default) or `thread`  
		`raiseExc`: Whether raise exception or not. Default: `True`  

	- **returns:**  
		The merged results from each job.  
  
!!! example "class: `Parallel`"
  
	A parallel runner  
  
	!!! abstract "method: `__init__ (self, nthread, backend, raiseExc)`"
  
		Constructor  

		- **params:**  
			`nthread` : Number of jobs to run simultaneously. Default: `1`  
			`backend` : The backend, either `process` (default) or `thread`  
			`raiseExc`: Whether raise exception or not. Default: `True`  
  
	!!! abstract "method: `run (self, func, args)`"
  
		Run parallel jobs  

		- **params:**  
			`func`    : The function to run  
			`args`    : The arguments for the function, should be a `list` with `tuple`s  
			`nthread` : Number of jobs to run simultaneously. Default: `1`  
			`backend` : The backend, either `process` (default) or `thread`  
			`raiseExc`: Whether raise exception or not. Default: `True`  

		- **returns:**  
			The merged results from each job.  
  
# module: pyppl.utils.ps
  
!!! example "function: `exists`"
  
	Check whether pid exists in the current process table.  
	From https://github.com/kennethreitz/delegator.py/blob/master/delegator.py  
  
!!! example "class: `Cmd`"
  
	A command (subprocess) wapper  
  
	!!! abstract "method: `__init__ (self, cmd, raiseExc, timeout, **kwargs)`"
  
		Constructor  

		- **params:**  
			`cmd`     : The command, could be a string or a list  
			`raiseExc`: raise the expcetion or not  
			`**kwargs`: other arguments for `Popen`  
  
	!!! abstract "method: `pipe (self, cmd, **kwargs)`"
  
		Pipe another command  

		- **examples:**  
			```python  
			c = Command('seq 1 3').pipe('grep 1').run()  
			c.stdout == '1\n'  
			```  

		- **params:**  
			`cmd`: The other command  
			`**kwargs`: Other arguments for `Popen` for the other command  

		- **returns:**  
			`Command` instance of the other command  
  
	!!! abstract "method: `run (self, bg)`"
  
		Wait for the command to run  

		- **params:**  
			`bg`: Run in background or not. Default: `False`  
				- If it is `True`, `rc` and `stdout/stderr` will be default (no value retrieved).  

		- **returns:**  
			`self`  
  
!!! example "function: `child`"
  
	Direct children  
  
# module: pyppl.utils.safefs
  
!!! example "function: `exists`"
  
	A shortcut of `SafeFs.exists`  

	- **params:**  
		`filepath`: The filepath  
		`callback`: The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if the file exists else `False`  
  
!!! example "function: `move`"
  
	A shortcut of `SafeFs.move`  

	- **params:**  
		`file1`    : File 1  
		`file2`    : File 2  
		`overwrite`: Whether overwrite file 2. Default: `True`  
		`callback` : The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if succeed else `False`  
  
!!! example "function: `gz`"
  
	A shortcut of `SafeFs.gz`  

	- **params:**  
		`file1`    : File 1  
		`file2`    : File 2  
		`overwrite`: Whether overwrite file 2. Default: `True`  
		`callback` : The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if succeed else `False`  
  
!!! example "class: `SafeFs`"
  
	A thread-safe file system  
  

	- **static variables:**  
  
		`TMPDIR`: The default temporary directory to store lock files  
  
		`FILETYPE_UNKNOWN`  : Unknown file type  
		`FILETYPE_NOENT`    : File does not exist  
		`FILETYPE_NOENTLINK`: A dead link (a link links to a non-existent file.  
		`FILETYPE_FILE`     : A regular file  
		`FILETYPE_FILELINK` : A link to a regular file  
		`FILETYPE_DIR`      : A regular directory  
		`FILETYPE_DIRLINK`  : A link to a regular directory  
  
		`FILES_DIFF_BOTHNOENT` : Two files are different and none of them exists  
		`FILES_DIFF_NOENT1`    : Two files are different but file1 does not exists  
		`FILES_DIFF_NOENT2`    : Two files are different but file2 does not exists  
		`FILES_DIFF_BOTHENT`   : Two files are different and both of them exist  
		`FILES_SAME_STRNOENT`  : Two files are the same string and it does not exist  
		`FILES_SAME_STRENT`    : Two files are the same string and it exists  
		`FILES_SAME_BOTHLINKS` : Two files link to one file  
		`FILES_SAME_BOTHLINKS1`: File1 links to file2, file2 links to a regular file  
		`FILES_SAME_BOTHLINKS2`: File2 links to file1, file1 links to a regular file  
		`FILES_SAME_REAL1`     : File2 links to file1, which a regular file  
		`FILES_SAME_REAL2`     : File1 links to file2, which a regular file  
  
		`LOCK`: A global lock ensures the locks are locked at the same time  
  
	!!! abstract "method: `__init__ (self, file1, file2, tmpdir)`"
  
		Constructor  

		- **params:**  
			`file1`:  File 1  
			`file2`:  File 2. Default: `None`  
			`tmpdir`: The temporary directory used to store lock files. Default: `None` (`SafeFs.TMPDIR`)  
  
	!!! abstract "staticmethod: `basename (filepath)`"
  
		Get the basename of a file  
		If it is a directory like '/a/b/c/', return `c`  

		- **params:**  
			`filepath`: The file path  

		- **returns:**  
			The basename  
  
	!!! abstract "method: `chmodX (self)`"
  
		Convert file1 to executable or add extract shebang to cmd line  

		- **returns:**  
			A list with or without the path of the interpreter as the first element and the script file as the last element  
  
	!!! abstract "method: `copy (self, overwrite, callback)`"
  
		Copy file1 to file2 thread-safely  

		- **params:**  
			`overwrite`: Allow overwrting file2? Default: `True`  
			`callback`:  The callback. arguments:  
				- `r` :  Whether the file exists  
				- `fs`:  This instance  

		- **returns:**  
			`True` if succeed else `False`  
  
	!!! abstract "method: `exists (self, callback)`"
  
		Tell if file1 exists thread-safely  

		- **params:**  
			`callback`: The callback. arguments:  
				- `r` : Whether the file exists  
				- `fs`: This instance  

		- **returns:**  
			`True` if exists else `False`  
  
	!!! abstract "method: `filesig (self, dirsig)`"
  
		Generate a signature for a file  

		- **params:**  
			`dirsig`: Whether expand the directory? Default: True  

		- **returns:**  
			The signature  
  
	!!! abstract "staticmethod: `flush (fd, lastmsg, end)`"
  
		Flush a file descriptor  

		- **params:**  
			`fd`     : The file handler  
			`lastmsg`: The remaining content of last flush  
			`end`    : The file ends? Default: `False`  
  
	!!! abstract "method: `gz (self, overwrite, callback)`"
  
		Gzip file1 (tar-gzip if file1 is a directory) to file2 in a thread-safe way  

		- **params:**  
			`overwrite`: Allow overwrting file2? Default: `True`  
			`callback`:  The callback. arguments:  
				- `r` :  Whether the file exists  
				- `fs`:  This instance  

		- **returns:**  
			`True` if succeed else `False`  
  
	!!! abstract "method: `link (self, overwrite, callback)`"
  
		Link file1 to file2 thread-safely  

		- **params:**  
			`overwrite`: Allow overwrting file2? Default: `True`  
			`callback`:  The callback. arguments:  
				- `r` :  Whether the file exists  
				- `fs`:  This instance  

		- **returns:**  
			`True` if succeed else `False`  
  
	!!! abstract "method: `move (self, overwrite, callback)`"
  
		Move file1 to file2 thread-safely  

		- **params:**  
			`overwrite`: Allow overwrting file2? Default: `True`  
			`callback`:  The callback. arguments:  
				- `r` :  Whether the file exists  
				- `fs`:  This instance  

		- **returns:**  
			`True` if succeed else `False`  
  
	!!! abstract "method: `moveWithLink (self, overwrite, callback)`"
  
		Move file1 to file2 and link file2 to file1 in a thread-safe way  

		- **params:**  
			`overwrite`: Allow overwrting file2? Default: `True`  
			`callback`:  The callback. arguments:  
				- `r` :  Whether the file exists  
				- `fs`:  This instance  

		- **returns:**  
			`True` if succeed else `False`  
  
	!!! abstract "method: `remove (self, callback)`"
  
		Remove file1 thread-safely  

		- **params:**  
			`callback`: The callback. arguments:  
				- `r` : Whether the file exists  
				- `fs`: This instance  

		- **returns:**  
			`True` if succeed else `False`  
  
	!!! abstract "method: `samefile (self, callback)`"
  
		Tell if file1 and file2 are the same file in a thread-safe way  

		- **params:**  
			`callback`: The callback. arguments:  
				- `r` : Whether the file exists  
				- `fs`: This instance  

		- **returns:**  
			`True` if they are the same file else `False`  
  
	!!! abstract "method: `ungz (self, overwrite, callback)`"
  
		Ungzip file1 (tar-ungzip if file1 tar-gzipped to file2 in a thread-safe way  

		- **params:**  
			`overwrite`: Allow overwrting file2? Default: `True`  
			`callback`:  The callback. arguments:  
				- `r` :  Whether the file exists  
				- `fs`:  This instance  

		- **returns:**  
			`True` if succeed else `False`  
  
!!! example "function: `ungz`"
  
	A shortcut of `SafeFs.ungz`  

	- **params:**  
		`file1`    : File 1  
		`file2`    : File 2  
		`overwrite`: Whether overwrite file 2. Default: `True`  
		`callback` : The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if succeed else `False`  
  
!!! example "function: `moveWithLink`"
  
	A shortcut of `SafeFs.moveWithLink`  

	- **params:**  
		`file1`    : File 1  
		`file2`    : File 2  
		`overwrite`: Whether overwrite file 2. Default: `True`  
		`callback` : The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if succeed else `False`  
  
!!! example "function: `link`"
  
	A shortcut of `SafeFs.link`  

	- **params:**  
		`file1`    : File 1  
		`file2`    : File 2  
		`overwrite`: Whether overwrite file 2. Default: `True`  
		`callback` : The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if succeed else `False`  
  
!!! example "function: `copy`"
  
	A shortcut of `SafeFs.copy`  

	- **params:**  
		`file1`    : File 1  
		`file2`    : File 2  
		`overwrite`: Whether overwrite file 2. Default: `True`  
		`callback` : The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if succeed else `False`  
  
!!! example "function: `remove`"
  
	A shortcut of `SafeFs.remove`  

	- **params:**  
		`filepath`: The filepath  
		`callback`: The callback. arguments:  
			- `r` : Whether the file exists  
			- `fs`: This instance  

	- **returns:**  
		`True` if succeed else `False`  
  
