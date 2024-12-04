# inventory.py

import pygame
import config
capacity = 20

class Inventory:
    def __init__(self):
        self.items = []
        self.capacity = capacity  # Maximum number of items allowed
        self.categories = {}
        self.selected_item = None  # Track selected item for usage
    
    def add_item(self, item, game=None):
        if len(self.items) >= self.capacity:
            print(f"Cannot add {item.item_type}: Inventory is full.")
            if game:
                game.add_notification("Inventory is full! Cannot pick up the item.")
            return False  # Indicate that the item was not added
        self.items.append(item)
        category = self.get_category(item.item_type)
        if category:
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(item)
        print(f"Added {item.item_type} to inventory.")
        return True  # Indicate successful addition
    
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            category = self.get_category(item.item_type)
            if category and item in self.categories.get(category, []):
                self.categories[category].remove(item)
            print(f"Removed {item.item_type} from inventory.")
    
    def has_item(self, item_type):
        return any(item.item_type == item_type for item in self.items)
    
    def get_items(self):
        return self.items
    
    def get_category(self, item_type):
        """
        Define categories based on item types.
        """
        categories = {
            'mushroom': 'Consumables',
            # Add other item types and their categories here
        }
        return categories.get(item_type, None)
    
    def use_item(self, player, item):
        """
        Use an item from the inventory, triggering its effect.
        """
        if item.usable:
            if item.item_type == 'mushroom':
                player.consume_mushroom(item)
                self.remove_item(item)
                print(f"Used {item.item_type}.")
            # Add other item types and their usage here
    
    def draw(self, surface):
        """
        Draw the inventory on the given surface.
        """
        font = pygame.font.SysFont('Arial', 20)
        inventory_surface = pygame.Surface((250, 400))
        inventory_surface.set_alpha(220)  # More opaque for better visibility
        inventory_surface.fill(config.BLACK)
        
        # Draw border
        pygame.draw.rect(inventory_surface, config.WHITE, inventory_surface.get_rect(), 2)
        
        surface.blit(inventory_surface, (config.WIDTH - 270, 10))  # Position at top-right corner

        # Display Inventory Title
        title = font.render("Inventory", True, config.YELLOW)
        surface.blit(title, (config.WIDTH - 260, 20))
        
        # Display Inventory Capacity
        capacity_text = font.render(f"Items: {len(self.items)}/{self.capacity}", True, config.WHITE)
        surface.blit(capacity_text, (config.WIDTH - 260, 50))

        y_offset = 80
        for category, items in self.categories.items():
            # Display category title
            category_text = font.render(category, True, config.WHITE)
            surface.blit(category_text, (config.WIDTH - 260, y_offset))
            y_offset += 25
            
            for item in items:
                # Load the item's image
                if item.item_type == 'mushroom':
                    if 'mushroom' in item.images and item.images['mushroom']:
                        item_image = item.get_image()
                    else:
                        item_image = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                        item_image.fill((255, 0, 0))  # Red fallback
                else:
                    # Default fallback for other items
                    item_image = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                    item_image.fill(config.WHITE)
                
                # Blit the item image
                surface.blit(item_image, (config.WIDTH - 260, y_offset))

                # Display the item name next to the icon
                item_text = font.render(item.item_type.capitalize(), True, config.WHITE)
                surface.blit(item_text, (config.WIDTH - 230, y_offset + 5))

                y_offset += 30  # Space between items
    # Optional: Implement Mouse Interaction for Using Items
    def handle_mouse_click(self, mouse_pos, player):
        """
        Handle mouse clicks within the inventory to select and use items.
        """
        inventory_x, inventory_y = config.WIDTH - 270, 10
        for category, items in self.categories.items():
            category_y = inventory_y + 25
            for item in items:
                item_rect = pygame.Rect(inventory_x, category_y, config.TILE_SIZE, config.TILE_SIZE)
                if item_rect.collidepoint(mouse_pos):
                    self.use_item(player, item)
                    break
                category_y += 30

