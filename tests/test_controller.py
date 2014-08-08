from kothlib import controller
import os
import time
import unittest
import logging

class RockPaperScissorsGame:
    valid_choices = ('rock', 'paper', 'scissors')
    wins = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}

    def __init__(self):
        self._controller = controller.Controller()

    def start(self, rounds):
        controller = self._controller
        controller.collect(os.path.join(os.path.dirname(__file__), 'bots'), 'command.txt', exclude=[
            # 'player_a', 'player_b',
            # 'oldman',
        ])
        controller.sort()
        scores = {client: 0 for client in controller}
        for round in range(rounds):
            print('-' * 80)
            print('round', round)
            print('players:', [client.name for client in controller.iter_alive()])
            t0 = time.time()
            print('send: choose')
            controller.send_all('choose')
            controller.receive_all(timeout=1.0)
            choices = set()
            for client in controller.iter_alive():
                choice = client.result
                if choice not in self.valid_choices:
                    continue
                choices.add(choice)
                print(client.name, client.result)
            if len(choices) == 2:
                choice1, choice2 = choices
                winner_choice = choice2 if self.wins[choice1] == choice2 else choice1
                for client in controller.iter_alive():
                    if client.result == winner_choice:
                        scores[client] += 1
            t1 = time.time()
            print('time elapsed', t1 - t0, 'sec')
        controller.send_all('quit')
        for client, score in sorted(scores.items(), key=lambda x: x[1]):
            print(client.name, score)
        print('Game finished')
        controller.receive_all(timeout=1.0)
        controller.kill_all()


class TestController(unittest.TestCase):
    def test_rock_paper_scissor_game(self):
        game = RockPaperScissorsGame()
        game.start(5)
        game.start(3)
