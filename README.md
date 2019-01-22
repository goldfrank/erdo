# erdo

It's the first version, so let's call it 0.1

This is a library for evaluating and graphically displaying decision trees. 'Erdő' is the Hungarian word for forest; umlauts in software are obnoxious.

**I basically wrote this in an afternoon, so it probably has bugs.**
I'm not an extraordinarily good programmer. My code is not well-documented. That will improve, hopefully. Many things will improve, hopefully.

Erdo is written for Python 3.6. It uses Python 3 print and division, so you'll have to import those if you'd prefer to use it with Python 2.7.

## Dependencies

It has one Python library dependency:
graphviz

`pip install graphviz` worked for me to install it.

Separately, the Python graphviz library is dependent on graphviz itself: https://graphviz.gitlab.io/download/

Ubuntu 18.04's package manager can install graphviz using `sudo apt install graphviz` , if you use Windows or Mac, use the link above.


## Usage:
* Declare nodes. There are three types: decision, uncertainty, and value.
* Add nodes as children of other nodes
* Nodes should be delcared before adding them as children.
* Create the graph

**Quick example:**

Put erdo.py in your working directory, and import the library:
```python
from erdo import *
```

First, create two value nodes corresponding to "sunshine given outdoors" and "rain given outdoors" :
```python
sun_o = Value_node(1, name='Sunshine | Outdoors')
rain_o = Value_node(0, name='Rain | Outdoors')
```

Then, create an uncertainty node corresponding to "outdoors" and add the first two nodes as children:

```python
outdoors = Uncertainty_node(name='Outdoors')
outdoors.child(sun_o, .4)
outdoors.child(rain_o, .6)
```
Finally, graph it:

```python
create_graph(outdoors)
```
The output looks like this:

![erdo example](https://github.com/goldfrank/erdo/blob/master/example.png "erdo example")

Adding a few more nodes (see [party.py](https://github.com/goldfrank/erdo/blob/master/party.py) for a full example) will give us the party problem from _Foundations of Decision Analysis_ by Howard and Abbas.

![erdo example 2](https://github.com/goldfrank/erdo/blob/master/example2.png "erdo example 2")

There's also some limted and probably buggy support for [testing](https://github.com/goldfrank/erdo/blob/master/party_test.py) and [control](https://github.com/goldfrank/erdo/blob/master/party_control.py). And yes, indeed, the function for adding control is `summon_the_wizard`, because the [wizard](https://github.com/goldfrank/erdo/blob/master/wizard.png) can make anything happen*. 

*Howard and Abbas, _Foundations of Decision Analysis_, Figure 9.3 on page 179

## Goals

My goals for this were to make a way to layout decision trees with concise and human-readable code, and generate human-readable graphic output. This is basically working, but probably fails in some cases. Please tell me if you find a failure case!

I have some additional goals, including:
* Generally the layout look better and more professional
* Generate sub-graphs for more easily-printed output. Large graphs display as one enormous image.
* Handle probabilistic uncertainty nodes. Right now, everythjing is either binomial or multinomial.
* Handle non-binomial tests
* Handle bayesian influence diagrams-- be able to display the same problem in both formats.

I'll probably get to some of them in the future.
