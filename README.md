# bac
This readme will focus on how the application flows.  First, let's start with
the command line:


bac [options] file0 [file1 file2 ...]


This is a change with the original as I will use stdin.  There will always
be an expectation of a file.  Files will have the form of name.abc or just
name

## A translation project
This is a translation project, taking the existing copy of abctab2ps
and translating it from C language to the Python language.  

## Sturctural changes