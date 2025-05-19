class Player:
    def __init__(self, health = 100, max_items = 2):
        self.max_items = max_items
        self.health = health
        self.inventory = {"stone": 1, "laser_gun": 0, "facility_key": 0}

    # Health Functions
    def lose_health(self, health_to_lose):
        self.health -= health_to_lose
    def gain_health(self):
        if self.health < 150:
            self.health += 50
            return f"Health: {self.health}" 
        elif self.health < 200:
            self.health = 200
            return f"Health: {self.health} Your health is now maxxed out."
        else:
            return "Your health is already maxxed out!"
    def add_item(self, item):
        self.inventory[item] += 1
    def use_item(self, item):
        pass
    def remove_item(self, item):
        self.inventory[item] -= 1
    def debug(self):
        pass


