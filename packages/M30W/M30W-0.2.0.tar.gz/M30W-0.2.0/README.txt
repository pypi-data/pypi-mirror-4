Welcome to M30W!

M30W is a program designed to allow fast developing of Scratch projects.
It uses a unique text syntax to allow typing of blocks rather than laggy
dragging them around.

M30W currently is in development process, and we haven't implemented
running scripts yet; Don't look for the green flag ;)
Editing scripts is working, but because we use kurt to parse scripts, 
current limitations apply:

- Take care with the "length of" block: strings aren't dropdowns, lists are

- length of [Hello!]      // string
- length of [list v]      // list

- Variable names (and possibly other values, such as broadcasts) can't:
  * contain special identifiers (like end, if, etc.)
  * have trailing whitespace
  * contain special characters, rather obviously: like any of []()<> or equals =
  * be named after a block, eg. a variable called "wait until"