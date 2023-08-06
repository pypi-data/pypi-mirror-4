![Trivio Logo](http://www.triv.io/images/trivio_logo.png)


Example Workflow
===


We're making managing a big data project as simple as a "git push". Think of us as "Heroku for Big Data"


With triv.io you can transform massive amounts of poorly structured data on a regular basis. Regardless of the size and whether your data exists in log files, multiple databases or even at the end of a web API we help you store, transform and share your data with others.

Install triv.io and login
---
``` 
$ pip install trivio
$ trivio login
  Triv.io uses github for authentication. You'll need a github 
  username and password to proceed. Authentication is done directly
  with the github servers, we never see or store your user name and
  password. Don't believe us? Have a look at the trivio client source.
  
  Github username: 
  Git hub password:
``` 

Create your first project
---
``` 
$ trivio create https://github.com/trivio/hello_world
Creating project hello_world
You do not have write access to this project
would you like to fork it?[Yn]: Y

forking project to https://github.com/username/hello_world
cloning  https://github.com/username/hello_world
Your project is ready for use
``` 

Try it out
---
```
~ $ cd hello_world 
hello_world $ trivio simulate word_counts
blah 1
foo 120
baz 767
```

Make some changes
---
Using your favorite editor let's make word_counts use a better tokenizer

```
hello_world $ ls
 word_counts.pyj
hello_world $ vi word_counts.pyj
```

Change the file to look like this

```
@word_counts.map
def map(doc, params,   tokenizer = re.compile('[^A-Z0-9_.]+', flags=re.I)):
  for word in tokenizer.split(doc['payload']):
    yield word, 1
```

Now run simulate again to verify the results

```
hello_world $ trivio simulate word_counts
blah 1
foo 120
baz 767
```

Push your changes
---
Once you've tweaked your algorithm you need to push those changes to trivio

```
hello_world $ trivio push "Used a better tokenizer"
changing to srobertson
[master 37200ed] pushing
 1 files changed, 1 insertions(+), 1 deletions(-)
Counting objects: 5, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 301 bytes, done.
Total 3 (delta 2), reused 0 (delta 0)
To git@github.com:srobertson/common_crawl_index.git
   4ebf177..37200ed  master -> master

Successfully pushed your changes to trivio.

Your project is paused use 'trivio step' or 'trivio resume' to build using
your changes.

hello_world $
```


Compute a single segment
---
By default, all projects start off "paused", this prevents them from running up your compute bills until you're satisfied your code works the way you expect it to. You've already used the `trivio simulate` method which samples your data and returns you results. The next step is to build a segment ("a portion of your table"see triv.io data model for more details)

```
$ trivio step word_counts
Building next segment 2009-9-17 00:00:00
$
```

Notice that this command returns immediately, building a segment can be quite involved. You may be producing terabytes of data which you wouldn't want to download to your workstation.

Monitoring Build Progress
---
```
$ trivio watch

Table                       Queued     Built Failed 
---------------------------------------------------
.../common-crawl/parsed-output    0        1      0


Next build: Never (project paused)
```

This will monitor your progress of your project. When the watch command spits out Next build Never. Hit `ctrl-c` to get back to your command line. As noted your project is paused so it won't build anything else until you either tell trivio to build a single segment with the step command or tell trivio to unpause your project. We'll get to unpausing in a moment


Querying tables
---

Now that trivio has had a chance to build part of your table we can query it for data. Tri.vio uses a sql like syntax for querying

```
$ trivio query "select * from word_counts"

+----------+-------+
|   key    | value |
+----------+-------+
| Zachary  | 22731 |
| Alfred   | 20477 |
| Gregory  | 17179 |
| Ned      | 16860 |
| Ulrich   | 15300 |
| Thomas   | 14995 |
+----------+-------+
```

Put Triv.io on Autopilot
---

Once you're happy with your project, you can tell triv.io to keep your tables up to date automatically based on the schedules you defined in your scripts.

```
$ trivio resume
Auto building all tables, use 'trivio watch' to monitor progress
```

Where to go from here
---
That's the basic workflow

* [Trivio data model](http://docs.triv.io/)
* [Talking to new storages](http://docs.triv.io/)
* [Interpreting mime types](http://docs.triv.io/)
* Check out our [blog](http://docs.triv.io/) for cool projects, tips and tricks


