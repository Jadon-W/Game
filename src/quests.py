# quests.py

import random
import config
import pygame

class Quest:
    def __init__(self, quest_type, description, objective, reward, target):
        self.quest_type = quest_type
        self.description = description
        self.objective = objective
        self.reward = reward
        self.completed = False
        self.progress = 0
        self.target = target  # Numeric target for collection/combat quests

    def is_completed(self):
        if isinstance(self.target, int):
            return self.progress >= self.target
        return False

    def complete_quest(self, player, game=None):
        if not self.completed:
            self.completed = True
            self.give_reward(player, game)
            print(f"Quest '{self.description}' completed!")

    def update_progress(self, player, world):
        if self.quest_type == 'collection':
            # Already handled in QuestManager
            pass
        elif self.quest_type == 'combat':
            # Handle combat quests (to be implemented later)
            pass
        # Add other quest types as needed
    def get_status(self):
        """
        Returns the quest status as a string.
        """
        return f"{self.description} [{self.progress}/{self.target}]"

    def give_reward(self, player, game=None):
        """
        Assign rewards to the player upon quest completion.
        """
        xp = self.reward.get('xp', 0)
        gold = self.reward.get('gold', 0)
        abilities = self.reward.get('abilities', [])
        items = self.reward.get('items', [])
        player.xp += xp
        player.gold += gold
        # Grant abilities
        for ability in abilities:
            player.grant_ability(ability)
        # Grant items
        for item in items:
            player.inventory.add_item(item)
        print(f"Received Reward: {xp} XP, {gold} Gold, {abilities}, {items}")
        
        # Add notifications if Game instance is provided
        if game:
            if abilities:
                for ability in abilities:
                    game.add_notification(f"New Ability Unlocked: {ability.capitalize()}")
            if xp > 0:
                game.add_notification(f"Received {xp} XP and {gold} Gold")

class QuestManager:
    def __init__(self):
        self.active_quests = []
        self.completed_quests = []

    def generate_quest(self, world):
        """
        Generate a new quest based on predefined quest types.
        """
        quest_type = random.choice(config.QUEST_TYPES)
    
        # Only allow quests that don't depend on special locations
        if quest_type in ['collection', 'combat']:
            description = config.QUEST_DESCRIPTIONS[quest_type]
            objective = config.QUEST_OBJECTIVES[quest_type]
            reward = config.QUEST_REWARDS[quest_type]
            target = self.extract_numeric_target(objective)
    
            quest = Quest(quest_type, description, objective, reward, target)
            self.active_quests.append(quest)
            print(f"New Quest Added: {quest.description}")
    
            # If the quest is a collection quest for mushrooms, spawn mushrooms
            if quest_type == 'collection':
                world.spawn_mushrooms(target)
        else:
            # Skip generating location-based quests for now
            self.generate_quest(world)  # Recursive call to generate a valid quest
    def extract_numeric_target(self, objective):
        """
        Extract numeric target from objective string.
        """
        words = objective.split()
        for word in words:
            if word.isdigit():
                return int(word)
        return 1  # Default target if none found

    def update_quests(self, player, world, game):
        """
        Update all active quests and handle completion.
        """
        for quest in self.active_quests[:]:
            if quest.quest_type == 'collection':
                # Check if player has collected a mushroom
                collected_items = pygame.sprite.spritecollide(player, world.active_items, True)
                for item in collected_items:
                    if item.item_type == 'mushroom':
                        # Attempt to add the item to inventory
                        added = player.inventory.add_item(item, game)
                        if added:
                            quest.progress += 1
                            print(f"Quest Progress Updated: {quest.description} [{quest.progress}/{quest.target}]")
                            if quest.is_completed():
                                quest.complete_quest(player, game)  # Pass Game instance
                                self.active_quests.remove(quest)
                                self.completed_quests.append(quest)
                                print(f"Quest Completed: {quest.description}")
                                self.generate_quest(world)
                        else:
                            # If not added, re-add the item to active_items so it remains on the map
                            world.active_items.add(item)
                            print(f"{item.item_type.capitalize()} remains on the ground as inventory is full.")
            elif quest.quest_type == 'combat':
                # Handle combat quests (to be implemented later)
                pass
            # Add other quest types as needed

    def handle_item_collection(self, player, world, item):
        """
        Update quests based on the collected item.
        """
        for quest in self.active_quests:
            if quest.quest_type == 'collection' and quest.objective.lower().startswith('collect'):
                if hasattr(item, 'item_type') and item.item_type == 'herb':
                    quest.progress += 1
                    print(f"Progress Updated for Quest: {quest.description} [{quest.progress}/{quest.target}]")
                    if quest.is_completed():
                        quest.complete_quest(player)
                        self.active_quests.remove(quest)
                        self.completed_quests.append(quest)
                        print(f"Quest Completed: {quest.description}")
                        self.generate_quest(world)  # Generate a new quest upon completion


