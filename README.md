# econsim
Base for an economy simulator: has accounts and market implemented. Uses text interface to interact

Accountant tracks all the accounts, creating .acc (csv) database. Yes, it can be definitely done better
Market tracks all stock exchanges in .market (also csv) files
textapp.py has functions that allow all of this to actually work. If you want to start this piece of creative shit, do python textapp.py

What might be added:

class World takes a txt map to generate a world.
h == house. Player lives here and consumes Food
f == farm. Player uses his workforce and creates Food.

Player's logic:
1) Sell his workforce at wrk-rub to a farm
2) go to a farm
3) work at the farm
4) go to house
5) Buy food at fod-rub
6) consume food, workforce += 1

Farm's logic:
1) Buy x workforce at wrk-rub
2) wait until x workers work
3) create food
4) sell food at fod-rub
