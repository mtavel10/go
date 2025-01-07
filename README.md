# CMSC 14200 Course Project

Team members:
- Luke Jimenez (GUI)
- Maya Mustata (QA)
- Nehal Lodha (TUI)
- Maddy Tavel (BOT)

This project is a complete implementation of the ancient Chinese board game, Go. The game logic was worked on as a group, and each specialized feature listed above was created by each group member. 

The game is coded entirely in python and features involved object-oriented programming principles. Using the Abstract Base Class, GoBase, and the Board Class, the Go class is responsible for the entire game logic. The Go class itself takes advantage of python's class properties, typing, operational logic, and a recursive algorithm to check the scores of each player (see in territory method). 

My individual contribution allows the player to play a Go game against an automated Bot. I created two different strategies: a random move and a minimax_move. The first strategy selects a random move for the player, given the list of available moves on the board. The second strategy is "smarter", because it simulates a game given every available move, and selects the move with the highest average number of pieces on the board AFTER the opponent makes a move in response to the given move. To test this, I ran a game simulation from the command line where two bots competed against each other, one using the smart strategy and the other using the random one. 
