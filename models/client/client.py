import json
import socket

from threading import Thread

import pygame 


class Client(object):

    def __init__(self, server_path, name):
        self.players_props = {}
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip, self.port = server_path.split(':')

    def _send_to_server(self, data):
       self.socket.sendto(data, (self.ip, int(self.port))) 

    def _handle_client_events(self):
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.KEYDOWN:
            
            payload = {'name': self.name}

            if event.key == 273:
                payload['action'] = 'up'
            elif event.key == 274:
                payload['action'] = 'down'
            elif event.key == 275:
                payload['action'] = 'right'
            elif event.key == 276:
                payload['action'] = 'left'

            if 'action' in payload:
                self._send_to_server(json.dumps(payload).encode('utf-8'))

        return True

    def _update_player(self, decoded_data):
        player_name = decoded_data['name']
        server_x = decoded_data['x']
        server_y = decoded_data['y']

        if player_name not in self.players_props:
            self.players_props[player_name] = {
                'x': server_x,
                'y': server_y
            }
        else:
            self.players_props[player_name]['x'] = server_x
            self.players_props[player_name]['y'] = server_y
        
    def _rcv_from_server(self):
        
        while True:
            data, _ = self.socket.recvfrom(4096)
            decoded_data = json.loads(data)

            print(decoded_data)
            self._update_player(decoded_data)

    def _draw_map(self, window):
        window.fill((0, 255, 0, 255))

        surface = pygame.Surface((40, 40))
        for i in range(15):
            window.blit(surface, (i * 40, 0))
            window.blit(surface, (0, i * 40))
            window.blit(surface, (14 * 40, i * 40))
            window.blit(surface, (i * 40, 14 * 40))

    def run(self):
        pygame.init()
        window = pygame.display.set_mode((600, 600))

        rcv = Thread(target=self._rcv_from_server)
        rcv.start()

        while True:
            self._draw_map(window)

            keep_running = self._handle_client_events()
            if not keep_running:
                break

            for player_name in self.players_props:
                pos_x = self.players_props[player_name]['x']
                pos_y = self.players_props[player_name]['y']

                pygame.draw.circle(
                    window,
                    (255, 255, 255, 255),
                    (pos_x, pos_y),
                    20)

            pygame.display.update()

            print(self.players_props)

        pygame.quit()

