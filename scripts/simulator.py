import time
import copy
from statistics import mean
from random import shuffle
from IPython.display import clear_output

import pandas as pd

import scripts.graph as graph

class Simulator():
    """
    Simulator class that runs simulation of given packages for given graph
    """
    def __init__(self, G, packages):
        self.G = G
        self.packages = packages

    def infallibility(self):
        """
        Calculates infallibility of the graph, based on capacity and flows of the edges
        """
        g = sum(1 for p in self.packages if p.success == False)
        size_mean = mean(p.size for p in self.packages if p.success == False)
        edge_sum = sum(
            self.G[n1][n2]['flow']/
            (self.G[n1][n2]['capacity']/size_mean - self.G[n1][n2]['flow'])
            for (n1,n2) in self.G.edges()
        )

        return (1/g)*edge_sum

    def run(self, timeout, timelapse = 1, reload_flag = False, draw = True):
        """
        Runs simulation for simulator object.
        :param int timeout - how many rounds should the simulation take
        :param int timelapse - time of a round in seconds

        For each package the generator is being invoked once in each round.
        In each round the graph is being drawn with shown vertices and edges were
        currently packages are.
        """
        rounds = 0
        timer = 0
        infallibilities = []

        input_packages = copy.deepcopy(self.packages)
        package_routes = [(p,p.send(self.G)) for p in self.packages]

        while (False in [p.success for p in self.packages]) and timer < timeout: 

            # Shuffling packages order, to simulate threading
            shuffle(package_routes)
            for p, route in package_routes:
                if not p.success:
                    next(route)
    
            # Print updated graph
            if draw:
                clear_output(wait=True)
                graph.draw(self.G)
            rounds += 1

            # Incrementing timer and counting infallibility only on edge move
            if rounds % 2 == 0 and (False in [p.success for p in self.packages]):
                timer += 1
                infallibilities.append((timer, self.infallibility()))


            if draw:
                print("Timer: ", timer)

            time.sleep(timelapse)

            if reload_flag:
                reload_packages = copy.deepcopy(input_packages)
                self.packages.extend(reload_packages)
                package_routes.extend([(p,p.send(self.G)) for p in reload_packages])
                
                


        # Printing statistics
        print("\n"+pd.DataFrame(infallibilities, columns=["Timer","Infallibilty"]).to_string(index=False))

        #data = [[p.source, p.target, p.time, p.success, p.waited] for p in self.packages]
        #df = pd.DataFrame(data, columns=["Source", "Target", "Time", "Success", "Waited"])
        #print("\n"+df.to_string(index=False))

        print("Waited: ", sum(1 for p in self.packages if p.waited == True))