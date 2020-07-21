# CodeArgos
This tool supports the continious recon of scripts and script blocks in an active web application. 

It populates and maintains an internal database by web crawling a target and detects Javascript files and HTML script blocks, watching for changes as they are published. 

The tool can then produce change diffs between scansets to allow security researchers to pinpoint the changing attack surface of the target web application.
## Install
Install using:
```bash 
git clone https://github.com/DanaEpp/CodeArgos.git 
cd CodeArgos
python3 setup.py install 
```
Dependencies will be installed and `codeargos` will be added to your path.

To create a cron job that will run CodeArgos every day:
```bash
crontab -e
```
Then create an entry that looks something like this:

```bash
@daily python3 -m /path/to/codeargos -u https://yourtarget.com
```

This will run CodeArgos once a day, at midnight against your target web app. You can adjust the schedule to meet your needs, and add additional arguments as needed (defined below).

**NOTE:** If you are using CodeArgos against several different targets, try to schedule recon scan windows at least 30 minutes apart. This will allow CodeArgos to maximize your CPU, threads and bandwidth during the web crawling of each target.

## Usage
```bash 
python3 -m codeargos -u target.com [-t thread_cnt] [-d] [-s] [-f /path/to/your/file.db] [-w slack --wurl=https://hook.slack.com/some/webhook]
```
* `-u`, `--url` : The target base URL (with crawl anything it finds underneith it)
* `-t`, `--threads` [optional] : The number of threads to run. By default it is calculated at 5 times your total CPU count
* `-d`, `--debug` [optional] : Write out debug information to local log file (codeargos.log)
* `-s`, `--stats` [optional] : Dump stats to stdout to show progress of crawl
* `-f`, `--file` [optional] : Reads and stores data across runs using a sqlite database you point to. If not used, default is `target.com.db`, where **target** is the hostname of the URL passed in.
* `-w`, `--webhook` [optional] : Enables notifications to a webhook. Possible options are *slack*, *teams*, *discord* and *generic*. Requires the `--wurl` param. Use generic when sending to Zapier, IFTTT, Microsoft Logic Apps or Microsoft Flow
* `--wurl` or `webhookurl` [optional] : The fully qualified path to your webhook endpoint. You need to generate this in your favorite web app (Slack/Teams/Discord etc).

## Webhooks support
For more information on setting up webhook notifications for your favorite apps please see:
* **Slack** : [Detailed instructions](https://api.slack.com/messaging/webhooks). To setup your first one [go here](https://my.slack.com/services/new/incoming-webhook/).
* **Microsoft Teams** : TBA
* **Discord** : TBA
* **Generic webhook** : TBA

## Tips
If you are having any difficulties in crawling your target web app, consider dialing back the threads used. By default it will select five times the number of CPUs you have. I've found the most success with `-t 10` on targets behind difficult WAFs. While there is an incrimental backoff retry pattern in the tool, the reality is CodeArgos can be agressive on its initial scan as it populates it's database. 

If you aren't sure whats going on, use the `-d` argument and look through the `codeargos.log` file to see what is going on. ie: `tail -f codeargos.log` 

If you find the tool is tripping up on a target, please open an [issue](https://github.com/DanaEpp/CodeArgos/issues) and include your target URL and any log data you are comfortable in sharing. I'll try to take a look at it ASAP.

## Dev Tips
You can evaluate the scanner and parser by jumping into the test_site dir and running the launcher. It will load a test web server on port 9000 for you.

```
cd test_site
./launch_test_site.sh
```
In another shell window execute:
```
python3 -m codeargos -u http://localhost:9000 -d -t 10 -f test.db
```
The test site will continue to be expanded on as we find in-field issues with the parsing and data management. If you wish to contribute, here would be a great place to add complex and weird script blocks that we can evaluate and make sure get parsed correctly.

