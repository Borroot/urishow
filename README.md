
![](misc/showcase.gif)

# Urishow
Select a uri from an input stream and open it with the correct program, useful in Mutt.

## Installation
```
$ make
# make install
```

## Keybindings
```
k - up
j - down
u - up   half page
d - down half page
K - up   full page
J - down full page
g - first
G - last
H - top
M - middle
L - bottom
c - to clipboard
h - help
<0-9> - jump
q esc - exit
enter - select
```

## Usage
```sh
$ python main.py -f file.txt
$ cat file.txt | python main.py
```

```
usage: python main.py [-h] [-p] [-r REGEX] [-c COMMAND] [-f FILE]

Extract, show, select and launch uri's.

optional arguments:
  -h, --help  show this help message and exit
  -p          just print the extracted uri's
  -r REGEX    regex for extracting uri's
  -c COMMAND  command to launch uri
  -f FILE     file to extract uri's from
```
