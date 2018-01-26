# Attitude Change on ChangeMyView (CMV)

This is a code repository for the [Computation, Cognition, and Development Lab](https://www.cognitionasu.org/) at ASU. In this project, we are interested in studying how people's minds are changed on the popular Reddit forum [_Change My View_](https://www.reddit.com/r/changemyview/), which is a subreddit where users post their stance on issues with the understanding that others will attempt to change their view by providing arguments opposing their perspective.  As to be expected, some arguments are more convincing than others. And this project seeks to study the mechanisms that makes certain arguments more succesfull than others, and ultimately uncover the factors that drive belief change on the forum.

## Data
- Data we collected for this project can be found ![here](./data)

## Scripts 
- The code for this project can be found ![here](./scripts)
- ![This notebook](./scripts/evidence_use.ipynb) documents are we study evidence use and rates of belief change on _Change My View_

## Research & Publications
_exciting stuff is still to come!_

## Documentation & code walk-through

   ### Connecting to the Reddit API
   ### Traversing the discussion tree

   ### Determining user belief change

   ### Determining use of evidence
We consider evidence to be cited if a user does one of two things: (1) cite an external website using a hyperlink, and (2) use statistically oriented language. 

   #### Hyperlinks
   
The function `has_link` checks every word `w` used in a discussion to see if it contains one of the substrings that signifies a link to an external webpage.
``` python
def has_link(w):
    extensions = ['http://', '.com', '.org', '.gov', 'pdf', '.net', 'www.']
    if any(e in w for e in extensions) and not ('reddit.com' in w):
        return True
```

For a more detailed picture of how links are used in a total discussion on _Change My View_ we are interested in counting the total amount of links used in the discussion, `tot_link`, the amount of comments that cite at least one link, `com_links`, and the names of the websites a user links to, `links_list`. 

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
