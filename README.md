# CodeArgos
This tool supports the continious recon of scripts and script blocks in an active web application. 

It populates and maintains an internal database by web crawling a target and detects Javascript files and HTML script blocks, watching for changes as they are published. 

The tool can then produce change diffs between scansets to allow security researchers to pinpoint the changing attack surface of the target web application.
## Install
Install using:
```bash 
python3 setup.py install 
```
Dependencies will be installed and `codeargos` will be added to your path.
## Usage
```bash 
python3 -m codeargos -u target.com [-t thread_cnt] [-d] [-s] [-f /path/to/your/file.db]
```
* `-u`, `--url` : The target base URL (with crawl anything it finds underneith it)
* `-t`, `--threads` [optional] : The number of threads to run. By default it is calculated at 5 times your total CPU count
* `-d`, `--debug` [optional] : Write out debug information to local log file (codeargos.log)
* `-s`, `--stats` [optional] : Dump stats to stdout to show progress of crawl
* `-f`, `--file` [optional] : Reads and stores data across runs using a sqlite database you point to. If not used, default is `target.com.db`, where **target** is the hostname of the URL passed in.

## Tips
If you are having any difficulties in crawling your target web app, consider dialing back the threads used. By default it will select five times the number of CPUs you have. I've found the most success with `-t 10` on targets behind difficult WAFs. While there is an incrimental backoff retry pattern in the tool, the reality is CodeArgos can be agressive on its initial scan as it populates it's database. 

If you aren't sure whats going on, use the `-d` argument and look through the `codeargos.log` file to see what is going on. ie: `tail -f codeargos.log` 

If you find the tool is tripping up on a target, please open an [issue](https://github.com/DanaEpp/CodeArgos/issues) and include your target URL and any log data you are comfortable in sharing. I'll try to take a look at it ASAP.

