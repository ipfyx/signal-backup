## SIGNAL SAVE
Signal-backup is a python3 script to backup signal conversations, wether its a group or not, as html pages.

# Requirements
A signal backup (tested with Android) fully decrypted using [signal-backup-decode](https://github.com/pajowu/signal-backup-decode).

Usage : 
```
$ cat pass_signal
123451234512345123451234512345

$ signal-backup-decode --output-path out --password-file pass_signal signal-1970-01-01-01-00-00.backup
Database Version: ...
Copy successful, sqlite at signal-backup/out/signal_backup.db

$ ls -1 out
attachment/
avatar/
config/
stickers/
signal_backup.db
```

# Basic usage
```
$ python3 signal_backup.py -h
usage: signal_backup.py [-h] [--db DB_PATH] [--attachment ATTACHMENT_DIR] [--conv_name CONV_NAME [CONV_NAME ...]] [--yourself YOUR_NAME]
                      [--output_dir HTML_OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  --db DB_PATH          Path to signal_backup.db file
  --attachment ATTACHMENT_DIR, -a ATTACHMENT_DIR
                        Path to attachment directory
  --conv_name CONV_NAME [CONV_NAME ...], -cn CONV_NAME [CONV_NAME ...]
                        Name of the conversation you wish to display
  --yourself YOUR_NAME, -y YOUR_NAME
                        Your name
  --output_dir HTML_OUTPUT_DIR, -o HTML_OUTPUT_DIR
                        html output dir

ipfyx@mysecretmachine:~/signal/signal-backup$ ls -1
bootstrap
CSS.py
example
--> out
README.md
signal_backup.py
signal.css
signal_structure.py

python3 signal_backup.py --db out/signal_backup.db --attachment out/attachment/ -cn 'Conversation Name 1' "Conversation Name 2" -y 'Your Name' --o output_directory 
Creating outpur directory backup_1970-01-01/Conversation Name 1/
Saving conversation Conversation Name 1
Copying attachment to backup_1970-01-01/Conversation Name 1/Conversation Name 1
# Sometimes files are deleted Failed fo move ./out/attachment//1618845228949_15172.docx because it does not exist
#TODO File not found. Unknown file type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet for attachment 1618950490743_15207
3396 attachments successfuly copied
Conversation Conversation Name 1 successfuly saved
Creating outpur directory ...
Saving conversation ...
Copying attachment to ...
194 attachments successfuly copied
Conversation ... successfuly saved

ipfyx@mysecretmachine:~/signal/signal-backup$ ls -1
--> backup_1970-01-01
bootstrap
CSS.py
example
--> out
README.md
signal_backup.py
signal.css
signal_structure.py
```

# How does it work 
Signal-backup requests sms and mms in the database, their parts, their quotes etc. and format them in an html page using bootstrap. The parts are then copied from the attachment directory to the attachment directory in each conversation saved.

# Result
Here is the index html file it will generate. You can then click on any month to view the messages sent during that month, sender names were anonymised.
![Alt text](example/index.png?raw=true "index.html")
Here is the resulting conversation.
![Alt text](example/example.png?raw=true "conv_month.html")


# TODO
- Support color by contact
- Better embedding of mp4, pdf etc.
- Find and fix more bugs
- Feel free to contributes !
