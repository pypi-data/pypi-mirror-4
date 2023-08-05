Reporter
========

Flexible text extraction from HTML in Python.

In short, Reporter:

-	Extracts the main text from HTML.
-	Uses a white-box scoring algorithm to determine the main text container.
-	Can easily be extended.
-	Supports Unicode without pain.
-	Has awesome debugging facilities.


Background
----------
Reporter is being developed at [Visual Revenue, Inc.](http://www.visualrevenue.com) where it is used to extract the main text from news articles. 
The name Reporter and internal terms are inspired by the news domain.

Usage
-----

Reporter can be invoked from the command line:

	$ ./reporter.py --url URL

The HTML from URL will be parsed by [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/) and the main
text will be printed on stdout. If the **--debug** flag is added, the text
and HTML will be saved to file. The HTML will be styled as follows.
Each tag will get a background color based on its score, ranging from
red (low score) to green (high score). Moreover, the tag that is
selected as news container (see below) will have a blue dashed line.

If the **--test** flag is given, all files in ./test/input will be
processed, and the text and HTML will be saved, as in **--debug**. This is
useful for processing many local files, so that these only have to
downloaded once. 

Please see **./reporter.py --help** for more options.

Reporter can also be used from Python:

	my_reporter = Reporter()
	my_reporter.read(url='http://example.com')
	print my_reporter.report_news()

Please note that Reporter is not (yet) a Python package.


Scoring algorithm
-----------------

To extract the main text from an HTML document, Reporter gives each HTML
tag (e.g, DIV, H1, and P) a score. The text contained in the tag with
the highest score is returned as the main text of the news article.

The main part of the scoring algorithm is based on traversing the
parsed HTML and works as follows. Reporter traverses the HTML in
reverse order, i.e., it starts at the leafs of the DOM tree. Each tag
is scored either as a paragraph or as a container. A tag is considered
to be a paragraph (in the abstract sense, not in the P sense) when it
contains more than 10 characters\*, otherwise it is considered to be a
container. The exact scoring of a tag is defined in the **Autocue**. An
Autocue is a list of scoring rules that get triggered at various
stages. For example, when a tag is to be scored as a paragraph, one
rule may count the number of words and return 2 points per word. Once
a tag (and its siblings) are scored, its parent is scored. If the
parent is also considered to be a paragraph, which happens, for
instance, with the P tag in: 

	<DIV><P>Hello World, this is the <B>Reporter package</B></P></DIV>

the scores of the B tag are discarded and the complete text is re-scored. The DIV tag is scored as a container because (in this case) it contains no text by itself. In fact, there is
an important scoring rule which penalises containers. If such a rule
would not be included, the HTML tag would always receive the highest score,
which would not be very effective.

_\*) Currently, this is the only heuristic that is hard-coded. In
[Readability](https://github.com/gfxmonk/python-readability), which served as the inspiration for Reporter, all scoring is hard-coded._

As mentioned, a scoring rule is triggered at a certain stage as the
Reporter is processing the Autocue. Below, we list and explain the
seven triggers with Python code. (The complete default Autocue is in
**autocues.py**, which is easily extensible with additional rules.)


- **HTML**, operates on the raw HTML. For example: split a paragraph with two consecutive line breaks into two paragraphs

		default_autocue.append((RegExReplacer(pattern='<br */? *>[\\r\\n]\*<br */? *>', repl='</p><p>'), HTML))

- **PRE\_TRAVERSAL**, scores or prunes (deletes tags) before the DOM is traversed. This is useful for getting rid of specific tags such as footers, or give positive scores to certain tags For example, delete all comments (specific to a certain news property):
	default\_autocue.append((CSSSelector("div#comments", Pruner()),
PRE\_TRAVERSAL))

Now, the HTML will be traversed as explained above.

- **EVAL\_PARAGRAPH**, scores a tag as a paragraph. For example, by counting words.

		default\_autocue.append((Scorer(RegExMatcher("(\w)+(['`]\w)?", factor=2, name="word"), reset_children=True), EVAL_PARAGRAPH))

- **EVAL\_CONTAINER**, scores a tag as a container. For example, combining the scores of the children tags with a 70 points penalty, giving a minimal score of 0.

		default_autocue.append((ScoreAggregator(start_score=-70, vmin=0), EVAL_CONTAINER))

This concludes the traversing of the HTML.

- **POST\_TRAVERSAL**, scores or prunes tags after Reporter has traversed the HTML. 

The tag with the highest score is selected as news container.

- **NEWS\_CONTAINER** is like POST\_TRAVERSAL but only applies to the tag that is selected as news container.

  Example: penalize DIVs inside the news container:

		default_autocue.append((CSSSelector("div", Scorer(FixedValue(-60))), NEWS_CONTAINER))

  Example: Get rid of any tags that have a score below -50:

		default_autocue.append((ScoreSelector(threshold=-50, mode="upper", actor=Pruner()), NEWS_CONTAINER))

- **NEWS\_TEXT**, operates on the text inside the news container. For example, put all text on one line:

		default_autocue.append((RegExReplacer(pattern='\s+', repl=' '), NEWS_TEXT))

Now, we can return the final text as the main text of the HTML!


License
-------
BSD
