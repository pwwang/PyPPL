
You can ask `PyPPL` to terminate, retry or ignore a job that fails to run.
When a job finishes, it should generate a `job.rc` file containing the return code. When compare with the valid return codes `pXXX.rc`, the error triggered if it is not in `pXXX.rc`. `pXXX.errhow` determines what's next if errors happen.

- `"terminate"`: when errors happen, terminate the entire pipeline
- `"ignore"`   : ignore the errors,  continuing run the next process
- `"retry"`    : re-submit and run the job again. `pXXX.errntry` defines how many time to retry.
- `"halt"`     : try to halt the entire pipeline if any job encounters error.
