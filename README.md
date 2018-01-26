# Attitude Change on Change My View (CMV)

This is a code repository for the [Computation, Cognition, and Development Lab](https://www.cognitionasu.org/) at ASU. In this project, we are interested in studying how people's minds are changed on the popular Reddit forum [_Change My View_](https://www.reddit.com/r/changemyview/), which is a subreddit where users post their stance on issues with the understanding that others will attempt to change their view by providing arguments opposing their perspective.  As to be expected, some arguments are more convincing than others. And this project seeks to study the mechanisms that makes certain arguments more succesfull than others, and ultimately uncover the factors that drive belief change on the forum.

## Programming languages used
- Data collection and preperation was exectued with Python
- Data analysis, modeling, and visualization utilized R

## Data
- Data we collected for this project can be found [here](https://github.com/jpriniski/CMV/tree/master/data)

## Scripts 
- The code for this project can be found [here](https://github.com/jpriniski/CMV/tree/master/scripts)
- [This notebook](https://github.com/jpriniski/CMV/blob/master/scripts/evidence_use.ipynb) details how we studied evidence use and rates of belief change on _Change My View_

## Research & Publications
_exciting stuff is yet to come!_

## Documentation & code walk-through

### Connecting to the Reddit API
To collect posts to CMV and to collect the comments in every discussion, we connect to the Reddit API using the Python Reddit API Wrapper (PRAW).  Oauth encryption is used, so to connect to the API, you will need to have your own Reddit account and API credentials. After connecting to the Reddit API, we connect directly to our subreddit of interest: r/ChangeMyView.

```python
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     password='',
                     user_agent='',
                     username='')


subreddit = reddit.subreddit('changemyview')
```
### Determining user belief change
The [delta system](https://www.reddit.com/r/changemyview/wiki/deltasystem) is a way that users self track attitude change on _Change My View_. Users award comments deltas that change their minds.  Therefore, to track attitude change, we must track the comments that are awarded deltas.  

We first do this by checking if the delta bot, an automated delta awarder, signifies that a delta has been awarded. 
```python
def has_delta(body):
    if 'confirmed: 1 delta awarded to' in body.lower():
        return True
    return False
```
Once we find that a delta has been awarded in the discussion, we have to traverse updwards through the discussion tree until the root node (which signifies the comment that the a user awarded a delta to, a.k.a a _'delta awarded comment (DAC)'_) is encountered.  We then return the whole thread of discussion starting from DAC to the delta bot's awarding of the delta. 
```python
def set_value(value, value_list):
    value_list.append(value)
    return

def get_thread(comment, root, thread):
    if comment.parent() is root:
        return set_value(comment.body, thread)
    get_thread(comment.parent(), root, thread)
    set_value(comment.body, thread)

def get_delta_thread(post):
    post.comments.replace_more(limit = 0)
    queue = post.comments[:]
    threads = []
    root = post
    while queue:
        comment = queue.pop(0)
        if has_delta(comment.body):
            thread = []
            get_thread(comment, root, thread)
            threads.append(thread)
        queue.extend(comment.replies)
    
    return threads
```
We are also interested in the amount of deltas awarded in a given discussion. 
```python
def get_delta_count(comments):
    count = 0
    for comment in comments:
        if has_delta(comment):
            count += 1
    return count
```
### Determining use of evidence
We consider evidence use to consitute one of two things: (1) a user cites an external website using a hyperlink, or (2) a user uses statistically-oriented language. 
#### Hyperlinks
The function `has_link` checks every word `w` used in a discussion to see if it contains one of the substrings that signifies a link to an external webpage.
``` python
def has_link(w):
    extensions = ['http://', '.com', '.org', '.gov', 'pdf', '.net', 'www.']
    if any(e in w for e in extensions) and not ('reddit.com' in w):
        return True
```
To paint a more detailed picture of how links are used in a total discussion on _Change My View_ we are interested in counting the total amount of links used in the discussion, `tot_link`, the amount of comments that cite at least one link, `com_links`, and the names of the websites a user links to, `links_list`. 
``` python
def cnt_links(links):
    com_links = 0
    tot_links = 0
    links_list = []
    for l in links:
        if not (l == []):
            post_links = []
            for _ in l:
                post_links.append(_)
                tot_links +=1
            links_list.append(post_links)
            com_links += 1
    return com_links, tot_links, links_list
```
#### Statistically-oriented language
We consider statistically-oriented language to consist of the use of digits or commonly used data-oriented ans statistical words.  The functions `has_dig` and `has_stat_langauge` checks every word `w` used in a discussion to see if it contains one of the a digit or uses a commonly used staistical word.
```python
def has_dig(w):
    return any(ch.isdigit() for ch in w)

def has_stat_language(w):
    terms = ['data', 'stats', 'statistics', 'figures', '%', 'percent', 'average']
    if any(t in w for t in terms) or has_dig(w):
        return True
 ```
