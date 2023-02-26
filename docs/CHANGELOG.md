# Change Log

## 0.4.5

- 🚑 Fix banner alignment in terminal

## 0.4.4

- 🐛 Fix when cli plugin has no docstring
- 🚑 Exclude help from help sub-command itself
- 🚑 Add cli plugin docstring as sub-command description

## 0.4.3

- ⬆️ Bump `argx` to 0.2.2
- 🎨 Expose `parse_args()` to cli plugins

## 0.4.2

- ⬆️ Bump `argx` to 0.2

## 0.4.1

- 🐛 Fix cli plugin name

## 0.4.0

- ⬆️ Upgrade python-slugify to ^0.8
- ⬆️ Upgrade xqute to 0.1.4
- ⬆️ Upgrade varname to 0.11
- 💥 Use argx instead of pyparam

## 0.3.12

- ⬆️ Upgrade python-slugify to ^7

## 0.3.11

- 📝 Fix github workflow badges in README
- 🩹 Fix pandas warning when less-column data passed to channel

## 0.3.10

- ⬆️ Upgrade xqute to 0.1.3
- ⬆️ Upgrade datar to 0.11 and format test files
- ✨ Add cli command version to show versions of deps
- ➖ Remove rich as it is required by xqute already

## 0.3.9

- ⬆️ Bump pipda to 0.11
- ⬆️ Bump xqute to 0.1.2

## 0.3.8

- ⬆️ Pump xqute to 0.1.1

## 0.3.7

- ⬆️ Upgrade varname to 0.10

## 0.3.6

- ⬆️ Upgrade pipda to 0.7.2, varname to 0.9.1, datar to 0.9

## 0.3.5

- 🐛 Fix `nexts` being inherited for `Proc` subclasses

## 0.3.4

- ✨ Print pipen version in CLI: pipen plugins
- 🩹 Make use of full terminal width for non-panel elements in log
- 🩹 Extend width to 256 when terminal width cannot be detected while logging (most likely logging to a text file)

## 0.3.3

- ♿️ Change default log width to 100
- 🩹 Fix broken panel in log content with console width cannot be detected

## 0.3.2

- ⬆️ Upgrade rtoml to v0.8
- ⬆️ Upgrade pipda to v0.6

## 0.3.1

- 🩹 Hide config meta data in pipeline information

## 0.3.0

- ⬆️ Upgrade dependencies
- 📌 Use `rtoml` instead of `toml` (see https://github.com/pwwang/toml-bench)
- 🩹 Dump job signature to file directly instead of dump to a string first
- 👷 Add python 3.10 to CI
- 📝 Add dependencies badge to README.md

## 0.2.16

- 📌 Pin dep versions
- 🩹 Allow to set workdir from Pipen constructor

## 0.2.15

- 🩹 Fix `FutureWarning` in `Proc._compute_input()`
- 🩹 Add `__doc__` for `Proc.from_proc()`
- 📌 Pin deps for docs

## 0.2.14

- 🩹 Shorten pipeline info in log for long config options
- 🐛 Fix cached jobs being put into queue
- 🩹 Shorten job debug messages when hit limits
- 🚑 Remove sort_dicts for pprint.pformat for py3.7

## 0.2.13

- 🩹 Don't require `job.signature.toml` to force cache a job

## 0.2.12

- 🐛 Hotfix for typos in `Proc.__init_subclass__()`

## 0.2.11

- 🩹 Update `envs`, `plugin_opts` and `scheduler_opts` while subclassing processes.

## 0.2.10

- ✨ Add hook `on_proc_input_computed`
- 🩹 Default new process docstring to "Undescribed process."

## 0.2.9

- ✨ Allow `requires` to be set by `__setattr__()`

## 0.2.8

- 🩹 Forward fill na for input data

## 0.2.7

- 🩹 Fix process plugin_opts not inherited from pipeline

## 0.2.6

- 🎨 Make `pipen._build_proc_relationships()` public and don't rebuild the relations
- ✨ Allow pipenline name to be obtained from assignment

## 0.2.5

- 🩹 Allow relative script path to be inherited
- 🐛 Fix column order from depedency processes
- 🩹 Fix __doc__ not inherited for processes

## 0.2.4

- ✨ Add execution order for processes


## 0.2.3

- ⚡️Speed up package importing

## 0.2.2

- 🐛 Load CLI plugins at runtime


## 0.2.1

- 🎨 Allow CLI plugin to have different name than the command

## 0.2.0

- 💥 Restructure CLI plugins

## 0.1.4

- 🩹 Use brackets to indicate cached jobs
- 🩹 Run on_complete hook only when no exception happened
- 🩹 Let `on_proc_init` to modify process `workdir`
- 🐛 Fix when `nexts` affected by parent `nexts` assignment when parent in `__bases__`

## 0.1.3

- ✨ Add `on_proc_init()` hook to enables plugins to modify the default attributes of processes
- 💥 Rename `Proc.args` to `Proc.envs`

## 0.1.2

- 💥 Use `set_starts()` and `set_data()` to set start processes of a pipeline.

## 0.1.1

- 💥 Allow plugins to modify other configs via on_setup() hook
- 🎨 Move progress bar to the last
- 🩹 Warn when no input_data specified for start process
- 💬 Change end to export
- 🚚 Move on_init() so it's able to redefine default configs
- 💥 Change `exec_cmd` hook of cli plugin to `exec_command`


## 0.1.0

It's now fully documented. See documentations.

## 0.0.4
- Clear output if not cached.
- Make process running order fixed

## 0.0.3
- Fix caching issue
- Add singleton to proc to force singleton
- Log an empty line after all processes finish
- Allow input to be None
- Separate channels from different required procs
- Move proc prepare before run
- Change the order proc banner printing, making sure it prints before other logs for the proc
- FIx job not cached if input is missing
- Don't redirect output only if absolute path specified
- Make input files resolved(absolute path)
- Give more detailed ProcDependencyError
- Force job status to be failed when Ctrl + c
- Fix files for input when it is a pandas dataframe
- Add job name prefix for scheduler
- Adopt datar for channels

## 0.0.2
- Add on_proc_property_computed hook
- Add plugin options for pipen construct
- Keep args, envs, scheduler_opts and plugin_opts as Diot object for procs
- Fix shebang not working in script
- Make sure job rendering data are stringified.
- Move starts as a method so that pipelines can be initialized before processes.
- Use plyrda instead of siuba for channel
- Add template rendering error to indicate where the rendering error happens;
- Add succeeded to on_complete hook;
- Add hook on_proc_start;
- Add argument succedded for hook on_proc_done;
- Realign pipeline and proc names in progress bars
- Remove debug log in job preparing, which will appear on the top of the logs

## 0.0.1

- Reimplement PyPPL using asyncio
