# Automatic-Gameplay-using-MCTS-and-Minmax
The game rule is as followed : 
![image](https://github.com/za970120604/Automatic-Gameplay-using-MCTS-and-Minmax/assets/72210437/ba1bca1b-a6d3-489b-acc0-b3a627240131)

The communication between the game server and my program, running as a client, is via TCP.

In this game , I implement 2 kinds of strategies : MCTS and Min-max with alpha-beta pruning , and the performance anaylisis is provided in the reprt.pdf.

# How to compile your own agent and battle with others : 
1. Write AI code in function "GetStep" in Minmax.py(MCTS.py)
2. Modify idTeam as your .py file name in Step1 in STcpClient.py , and then compile them into .exe
3. Modify input.txt : For each player in input.txt , the first line needs to be the .py file name in Step1 and the second line is the path to the .exe generated from Step2.You can also modify the node number and random seed . 
![image](https://github.com/za970120604/Automatic-Gameplay-using-MCTS-and-Minmax/assets/72210437/464885f4-d944-43e3-aae8-38899f5dca82)

5. Run AI.exe . 




