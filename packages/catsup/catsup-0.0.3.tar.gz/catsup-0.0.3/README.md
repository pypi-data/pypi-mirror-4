#catsup

##License
Licensed under the MIT License.

##Install

Simple way using pip

```bash
pip install catsup
```

Or another hard way to install

```bash
git clone git://github.com/whtsky/catsup.git
cd catsup
python setup.py install
```

##Settings

The default settings file is at `~/.catsuprc`, you can specific it by passing `--settings=/path/to/settings` when executing `python -m catsup.app <server/deploy/webhook>`

##Run
```bash
python -m catsup.app server --port=8888
```

Then go to http://localhost:8888 to take a look at your own catsup:)

##How to write
catsup uses Markdown to write posts.
Filename should like 2000-01-01-catsup.md(year-month-day-title.md)
Example:

	#Title
	- tags: tag1, tag2, tag3
	
	----
	
	Content
	```python
	print "hi,I'm coding."
	```

### Post properties
catsup supports some post properties. Write them before "---" and start with "- ".
Example:

    - category: A Category
    - date: 2012-12-24
    - tags: tag1, tag2
    - comment: no

The `category` property defines the category of the post, but it's not used yet.

The `date` property can overwrite the date from the file name.

The `tags` property defines the tags of the post.

The `comment` property defines whether the post can be commented or not.

### Post excerpt
You can use `<!--more-->` to define an excerpt of a post. Any content before that will be used as excerpt of the post. And you can choose to display excerpt rather than full content on your homepage.

##Deploy a static blog
run`python -m catsup.app deploy`
And you can find your static blog in deploy/ .