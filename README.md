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
python3 -m codeargos -u target.com [-t thread_cnt] [-d] [-s]
```
* `-u`, `--url` : The target base URL (with crawl anything it finds underneith it)
* `-t`, `--threads` [optional] : The number of threads to run. By default it is calculated at 5 times your total CPU count
* `-d`, `--debug` [optional] : Write out debug information to local log file (codeargos.log)
* `-s`, `--stats` [optional] : Dump stats to stdout to show progress of crawl 
