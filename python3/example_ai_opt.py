from colorfight import Colorfight
import time
import random
from colorfight.constants import BLD_GOLD_MINE, BLD_ENERGY_WELL, BLD_FORTRESS

# Create a Colorfight Instance. This will be the object that you interact
# with.
game = Colorfight()

# Connect to the server. This will connect to the public room. If you want to
# join other rooms, you need to change the argument
game.connect(room = 'groupa')

# game.register should return True if succeed.
# As no duplicate usernames are allowed, a random integer string is appended
# to the example username. You don't need to do this, change the username
# to your ID.
# You need to set a password. For the example AI, the current time is used
# as the password. You should change it to something that will not change
# between runs so you can continue the game if disconnected

def optimizeBld (cell):
    e = cell.natural_energy
    g = cell.natural_gold
    if game.turn<100:
        if(g<3 and e <3):
            #return BLD_HOME
            #return BLD_FORTRESS
            print("fuck forts")
        if(g>(e+4)):
            return BLD_GOLD_MINE
        else:
            return BLD_ENERGY_WELL
    elif game.turn>100 and game.turn<350:
        print("midgame")
        if(g<3 and e <3):
            return BLD_GOLD_MINE
            print("fuck")
        if(g>(e-2)):
            return BLD_GOLD_MINE
        else:
            return BLD_ENERGY_WELL
    else:
        print("endgame")
        if(g<3 and e <3):
            return BLD_GOLD_MINE
        if(g>(e-4)):
            return BLD_GOLD_MINE
        else:
            return BLD_ENERGY_WELL

if game.register(username = 'thanos' , \
        password = "fuck"):
    # This is the game loop



    while True:

        if game.turn<100:

            # The command list we will send to the server
            cmd_list = []
            # The list of cells that we want to attack
            my_attack_list = []
            # update_turn() is required to get the latest information from the
            # server. This will halt the program until it receives the updated
            # information.
            # After update_turn(), game object will be updated.
            game.update_turn()

            # Check if you exist in the game. If not, wait for the next round.
            # You may not appear immediately after you join. But you should be
            # in the game after one round.
            if game.me == None:
                continue

            me = game.me

            # game.me.cells is a dict, where the keys are Position and the values
            # are MapCell. Get all my cells.
            for cell in game.me.cells.values():
                #if(cell.building.is_home):
                # Check the surrounding position
                for pos in cell.position.get_surrounding_cardinals():
                    # Get the MapCell object of that position
                    c = game.game_map[pos]
                    #print("attacking ({},{})".format(c.position.x, c.position.y))
                    friendly=0
                    for p in c.position.get_surrounding_cardinals():
                        if(game.game_map[p].owner==game.uid or game.game_map[p].owner==0):
                            friendly+=1
                    #print("friends",friendly)

                    # Attack if the cost is less than what I have, and the owner
                    # is not mine, and I have not attacked it in this round already
                    # We also try to keep our cell number under 100 to avoid tax
                    if c.attack_cost < me.energy and c.owner != game.uid \
                            and c.position not in my_attack_list \
                            and len(me.cells) < 300\
                            and len(my_attack_list)<6\
                            and friendly>2:
                        # Add the attack command in the command list
                        # Subtract the attack cost manually so I can keep track
                        # of the energy I have.
                        # Add the position to the attack list so I won't attack
                        # the same cell
                        acost = c.attack_cost
                        if(c.building.name == "home"):
                            acost = acost*3
                        cmd_list.append(game.attack(pos, acost))
                        print("We are attacking ({}, {}) with {} energy".format(pos.x, pos.y, c.attack_cost))
                        game.me.energy -= acost
                        my_attack_list.append(c.position)

                # If we can upgrade the building, upgrade it.
                # Notice can_update only checks for upper bound. You need to check
                # tech_level by yourself.
                if cell.building.can_upgrade and \
                        (cell.building.is_home) and \
                        cell.building.upgrade_gold < me.gold and \
                        cell.building.upgrade_energy < me.energy:
                    cmd_list.append(game.upgrade(cell.position))
                    print("We upgraded home at({}, {})".format(cell.position.x, cell.position.y))
                    me.gold   -= cell.building.upgrade_gold
                    me.energy -= cell.building.upgrade_energy



                if cell.building.can_upgrade and \
                        (cell.building.is_home or cell.building.level < me.tech_level) and \
                        cell.building.upgrade_gold < me.gold and \
                        cell.building.upgrade_energy < me.energy and\
                        game.turn<450 and \
                        len(cmd_list)<15:
                    cmd_list.append(game.upgrade(cell.position))
                    print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
                    me.gold   -= cell.building.upgrade_gold
                    me.energy -= cell.building.upgrade_energy

                # Build a random building if we have enough gold
                if cell.owner == me.uid and cell.building.is_empty and me.gold >= 100:
                    #building = random.choice([BLD_FORTRESS, BLD_GOLD_MINE, BLD_ENERGY_WELL])
                    building = optimizeBld(cell);
                    cmd_list.append(game.build(cell.position, building))
                    print("We build {} on ({}, {})".format(building, cell.position.x, cell.position.y))
                    me.gold -= 100


            # Send the command list to the server
            result = game.send_cmd(cmd_list)
            print(result)

        elif game.turn>=100 and game.turn<300:
            cmd_list = []
            my_attack_list = []
            game.update_turn()

            if game.me == None:
                continue

            me = game.me

            for cell in game.me.cells.values():
                for pos in cell.position.get_surrounding_cardinals():
                    c = game.game_map[pos]
                    friendly=0
                    for p in c.position.get_surrounding_cardinals():
                        if(game.game_map[p].owner==game.uid or game.game_map[p].owner==0):
                            friendly+=1
                    if c.attack_cost < me.energy and c.owner != game.uid \
                            and c.position not in my_attack_list \
                            and len(me.cells) < 360\
                            and len(my_attack_list)<15\
                            and friendly>0:

                        acost = c.attack_cost*1.1
                        if(friendly<4):
                            acost = acost*1.1
                        if(friendly<3):
                            acost = acost *1.3
                        if(friendly<2):
                            acost = acost *1.5

                        if(c.building.name == "home"):
                            acost = acost*1.5
                        acost = int(acost)
                        cmd_list.append(game.attack(pos, acost))
                        print("We are attacking ({}, {}) with {} energy".format(pos.x, pos.y,acost))
                        game.me.energy -= acost
                        my_attack_list.append(c.position)

                for p in cell.position.get_surrounding_cardinals():
                    if(game.game_map[p].owner==game.uid or game.game_map[p].owner==0):
                        friendly+=1
                if friendly<2:
                    #print("We are seld attacking {} with {} energy".format(cell.position ,acost))
                    cmd_list.append(game.attack((cell.position), (game.me.energy/15)/(len(my_attack_list)+1)))
                    my_attack_list.append(cell.position)


                if cell.building.can_upgrade and \
                        (cell.building.is_home) and \
                        cell.building.upgrade_gold < me.gold and \
                        cell.building.upgrade_energy < me.energy:
                    cmd_list.append(game.upgrade(cell.position))
                    print("We upgraded home at({}, {})".format(cell.position.x, cell.position.y))
                    me.gold   -= cell.building.upgrade_gold
                    me.energy -= cell.building.upgrade_energy


                if cell.building.can_upgrade and \
                        (cell.building.is_home or cell.building.level < me.tech_level) and \
                        cell.building.upgrade_gold < me.gold and \
                        cell.building.upgrade_energy < me.energy and\
                        game.turn<450 and \
                        len(cmd_list)<15:
                    cmd_list.append(game.upgrade(cell.position))
                    print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
                    me.gold   -= cell.building.upgrade_gold
                    me.energy -= cell.building.upgrade_energy

                # Build a random building if we have enough gold
                if cell.owner == me.uid and cell.building.is_empty and me.gold >= 100:
                    #building = random.choice([BLD_FORTRESS, BLD_GOLD_MINE, BLD_ENERGY_WELL])
                    building = optimizeBld(cell);
                    cmd_list.append(game.build(cell.position, building))
                    print("We build {} on ({}, {})".format(building, cell.position.x, cell.position.y))
                    me.gold -= 100


            # Send the command list to the server
            result = game.send_cmd(cmd_list)
            print(result)
        elif game.turn>=300 and game.turn<501:
            cmd_list = []
            my_attack_list = []
            game.update_turn()

            if game.me == None:
                continue
            me = game.me

            for cell in game.me.cells.values():
                for pos in cell.position.get_surrounding_cardinals():
                    c = game.game_map[pos]
                    friendly=0
                    for p in c.position.get_surrounding_cardinals():
                        if(game.game_map[p].owner==game.uid or game.game_map[p].owner==0):
                            friendly+=1
                    if c.attack_cost < me.energy and c.owner != game.uid \
                            and c.position not in my_attack_list \
                            and len(me.cells) < 500\
                            and len(my_attack_list)<6\
                            and friendly>1:

                        acost = c.attack_cost*1.1
                        if(friendly<4):
                            acost = acost*1.1
                        if(friendly<3):
                            acost = acost *1.3
                        if(friendly<2):
                            acost = acost *1.5

                        if(c.building.name == "home"):
                            acost = acost*1.5
                        acost = int(acost)
                        cmd_list.append(game.attack(pos, acost))
                        print("We are attacking ({}, {}) with {} energy".format(pos.x, pos.y,acost))
                        game.me.energy -= acost
                        my_attack_list.append(c.position)

                for p in cell.position.get_surrounding_cardinals():
                    if(game.game_map[p].owner==game.uid or game.game_map[p].owner==0):
                        friendly+=1
                if friendly<2:
                    #print("We are seld attacking {} with {} energy".format(cell.position,(game.me.energy/25)/len(my_attack_list)))
                    cmd_list.append(game.attack(cell.position, (game.me.energy/15)/(len(my_attack_list)+1)))
                    my_attack_list.append(cell.position)

                # If we can upgrade the building, upgrade it.
                # Notice can_update only checks for upper bound. You need to check
                # tech_level by yourself.
                if cell.building.can_upgrade and \
                        (cell.building.is_home) and \
                        cell.building.upgrade_gold < me.gold and \
                        cell.building.upgrade_energy < me.energy:
                    cmd_list.append(game.upgrade(cell.position))
                    print("We upgraded home at({}, {})".format(cell.position.x, cell.position.y))
                    me.gold   -= cell.building.upgrade_gold
                    me.energy -= cell.building.upgrade_energy



                if cell.building.can_upgrade and \
                        (cell.building.is_home or cell.building.level < me.tech_level) and \
                        cell.building.upgrade_gold < me.gold and \
                        cell.building.upgrade_energy < me.energy and\
                        game.turn<450 and \
                        len(cmd_list)<15:
                    cmd_list.append(game.upgrade(cell.position))
                    print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
                    me.gold   -= cell.building.upgrade_gold
                    me.energy -= cell.building.upgrade_energy

                # Build a random building if we have enough gold
                if cell.owner == me.uid and cell.building.is_empty and me.gold >= 100:
                    #building = random.choice([BLD_FORTRESS, BLD_GOLD_MINE, BLD_ENERGY_WELL])
                    building = optimizeBld(cell);
                    cmd_list.append(game.build(cell.position, building))
                    print("We build {} on ({}, {})".format(building, cell.position.x, cell.position.y))
                    me.gold -= 100


            # Send the command list to the server
            result = game.send_cmd(cmd_list)
            print(result)
