# pygrep

A python3 utility that searches for a pattern using a regular expression in lines of text, 
and prints the lines which contain matching text


**Usage examples:**

Search regex in list of files, highlight matched text in red color
```
./pygrep.py -r '\d{3}' -f file* -c
```

Search regex in string provided in STDIN, underline start of each matched text with '^'
after run this command, need to provide input and when done, type 'q' and Enter to start the search
```
./pygrep.py -r '\d{3}' -u
```


**Some implementation details:**

Using Factory design pattern to instantiate correct formatter at runtime, based on the cli option provided (i.e one of -c, -u, -m or none of those since are optional)
