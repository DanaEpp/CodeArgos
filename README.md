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
python3 -m codeargos -u target.com 
```
