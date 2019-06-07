# Quality check

Scripts for biobb WFs quality check and generation of results.

## Generate results

USAGE:
	* With JSON config file:

		python3 generate_results.py -c config.json -i input_path -o output.tgz

	* With JSON string:

		python3 generate_results.py -c '{}' -i input_path -o output.tgz