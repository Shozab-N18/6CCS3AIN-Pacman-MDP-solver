Some things that you may find helpful:

(a) To evaluate whether your code can win games in smallGrid, run:
python2 pacman.py -q -n 25 -p MDPAgent -l smallGrid OR 
python2 pacman.py -p MDPAgent -l smallGrid

-l is shorthand for -layout. -p is shorthand for -pacman. -q runs the game without the
interface (making it faster).

(b) To evaluate whether your code can win games in mediumClassic, run:
python2 pacman.py -q -n 25 -p MDPAgent -l mediumClassic OR
python2 pacman.py -p MDPAgent -l mediumClassic

The -n 25 runs 25 games in a row.
