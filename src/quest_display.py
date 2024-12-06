# quest_display.py

import pygame
import config

class QuestDisplay:
    def __init__(self, quest_manager, camera):
        self.quest_manager = quest_manager
        self.camera = camera
        self.font = pygame.font.SysFont('Arial', 20)
        self.large_font = pygame.font.SysFont('Arial', 25)
        self.option_font = pygame.font.SysFont('Arial', 25)  # Initialized option_font
        self.active = False  # Determines if the quest display is visible
        self.scroll_offset = 0  # For scroll functionality
        self.scroll_speed = 20  # Pixels per scroll
        self.max_display_height = config.HEIGHT - 100  # Adjust as needed
        self.quest_height = 80  # Increased for better visibility; adjust as needed
        self.search_query = ""
        self.filtered_quests = self.quest_manager.active_quests.copy()
        self.selected_quest = None  # For interactive quests
        self.sort_option = "All"  # Current sort option
        self.filter_option = "All"  # Current filter option
        self.sort_options = [
            "All", "Type: Collection", "Type: Combat", 
            "Type: Exploration", "Type: Delivery", 
            "Level: Low to High", "Level: High to Low"
        ]
        self.filter_options = [
            "All", "Type: Collection", "Type: Combat", 
            "Type: Exploration", "Type: Delivery", 
            "Status: Active", "Status: Completed"
        ]
        self.typing = False  # Flag to check if typing in search bar

        # Panel dimensions
        self.panel_width = min(400, config.WIDTH * 0.3)  # 30% of screen width or 400px max
        self.panel_height = config.HEIGHT - 100  # Adjust as needed
        self.panel_x = config.WIDTH - self.panel_width - 20  # 20 pixels from the right edge
        self.panel_y = 50  # 50 pixels from the top

        # Scrollbar properties
        self.scrollbar_width = 10
        self.scrollbar_color = (200, 200, 200)
        self.scrollbar_handle_color = (150, 150, 150)
        self.total_quests = len(self.filtered_quests)

    def toggle_display(self):
        self.active = not self.active
        if not self.active:
            self.selected_quest = None  # Reset selection when closing

    def handle_event(self, event):
        if not self.active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                # Check if click is within the search bar area
                search_bar_rect = pygame.Rect(self.panel_x + 10, self.panel_y + 40, self.panel_width - 20, 30)
                if search_bar_rect.collidepoint(mouse_x, mouse_y):
                    self.typing = True
                else:
                    self.typing = False

                # Check if click is on Sort Option
                sort_option_rect = pygame.Rect(self.panel_x + 90, self.panel_y + 70, 120, 40)
                if sort_option_rect.collidepoint(mouse_x, mouse_y):
                    current_index = self.sort_options.index(self.sort_option)
                    new_index = (current_index + 1) % len(self.sort_options)
                    self.sort_option = self.sort_options[new_index]
                    self.apply_sorting()

                # Check if click is on Filter Option
                filter_option_rect = pygame.Rect(self.panel_x + 90, self.panel_y + 110, 120, 40)
                if filter_option_rect.collidepoint(mouse_x, mouse_y):
                    current_index = self.filter_options.index(self.filter_option)
                    new_index = (current_index + 1) % len(self.filter_options)
                    self.filter_option = self.filter_options[new_index]
                    self.apply_filtering()

                # Check if click is on scrollbar handle
                scrollbar_rect = pygame.Rect(self.panel_x + self.panel_width - 15, self.panel_y + 150, self.scrollbar_width, 20)
                if scrollbar_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging_scrollbar = True
                    self.mouse_y_offset = mouse_y - scrollbar_rect.y
                else:
                    self.dragging_scrollbar = False

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_scrollbar = False

        elif event.type == pygame.MOUSEMOTION:
            if hasattr(self, 'dragging_scrollbar') and self.dragging_scrollbar:
                mouse_x, mouse_y = event.pos
                # Calculate new scroll_offset based on mouse position
                relative_y = mouse_y - self.panel_y - 150
                scroll_ratio = relative_y / (self.panel_height - 150)
                max_scroll = max(len(self.filtered_quests) * self.quest_height - self.panel_height + 150, 0)
                self.scroll_offset = int(scroll_ratio * max_scroll)
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        elif event.type == pygame.KEYDOWN:
            if self.typing:
                if event.key == pygame.K_RETURN:
                    self.typing = False
                elif event.key == pygame.K_BACKSPACE:
                    self.search_query = self.search_query[:-1]
                    self.update_filtered_quests()
                else:
                    if event.unicode.isprintable():
                        self.search_query += event.unicode
                        self.update_filtered_quests()
            else:
                if event.key == pygame.K_UP:
                    pass  # Removed handling for self.options
                elif event.key == pygame.K_DOWN:
                    pass  # Removed handling for self.options
                elif event.key == pygame.K_RETURN:
                    pass  # Removed handling for self.options

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
            elif event.button == 5:  # Scroll down
                max_scroll = max(len(self.filtered_quests) * self.quest_height - self.panel_height + 150, 0)
                self.scroll_offset = min(self.scroll_offset + self.scroll_speed, max_scroll)

    def update_filtered_quests(self):
        """
        Update the filtered quests based on the search query and current filter.
        """
        query = self.search_query.lower()
        if self.filter_option == "All":
            self.filtered_quests = self.quest_manager.active_quests.copy()
        elif self.filter_option.startswith("Type:"):
            quest_type = self.filter_option.split(": ")[1].lower()
            self.filtered_quests = [q for q in self.quest_manager.active_quests if q.quest_type == quest_type]
        elif self.filter_option.startswith("Status:"):
            status = self.filter_option.split(": ")[1].lower()
            if status == "active":
                self.filtered_quests = [q for q in self.quest_manager.active_quests if not q.completed]
            elif status == "completed":
                self.filtered_quests = [q for q in self.quest_manager.completed_quests if q.completed]

        # Apply search filtering
        if query:
            self.filtered_quests = [
                quest for quest in self.filtered_quests
                if query in quest.description.lower() or query in quest.quest_type.lower()
            ]

        # Apply sorting
        self.apply_sorting()

        # Reset scroll when filtering
        self.scroll_offset = 0

    def apply_sorting(self):
        """
        Sort the filtered quests based on the selected sort option.
        """
        if self.sort_option == "All":
            pass  # No sorting
        elif self.sort_option.startswith("Type:"):
            quest_type = self.sort_option.split(": ")[1].lower()
            self.filtered_quests = sorted(
                self.filtered_quests,
                key=lambda q: q.quest_type == quest_type,
                reverse=True
            )
        elif self.sort_option.startswith("Level:"):
            order = self.sort_option.split(": ")[1]
            if order == "Low to High":
                self.filtered_quests = sorted(self.filtered_quests, key=lambda q: q.target)
            elif order == "High to Low":
                self.filtered_quests = sorted(self.filtered_quests, key=lambda q: q.target, reverse=True)

    def apply_filtering(self):
        """
        Filter the active quests based on the selected filter option.
        """
        if self.filter_option == "All":
            self.filtered_quests = self.quest_manager.active_quests.copy()
        elif self.filter_option == "Type: Collection":
            self.filtered_quests = [q for q in self.quest_manager.active_quests if q.quest_type == 'collection']
        elif self.filter_option == "Type: Combat":
            self.filtered_quests = [q for q in self.quest_manager.active_quests if q.quest_type == 'combat']
        elif self.filter_option == "Type: Exploration":
            self.filtered_quests = [q for q in self.quest_manager.active_quests if q.quest_type == 'exploration']
        elif self.filter_option == "Type: Delivery":
            self.filtered_quests = [q for q in self.quest_manager.active_quests if q.quest_type == 'delivery']
        elif self.filter_option == "Status: Active":
            self.filtered_quests = [q for q in self.quest_manager.active_quests if not q.completed]
        elif self.filter_option == "Status: Completed":
            self.filtered_quests = [q for q in self.quest_manager.completed_quests if q.completed]

        # Apply search filtering after main filtering
        if self.search_query:
            query = self.search_query.lower()
            self.filtered_quests = [
                quest for quest in self.filtered_quests
                if query in quest.description.lower() or query in quest.quest_type.lower()
            ]

        # Apply sorting after filtering
        self.apply_sorting()

        # Reset scroll when filtering
        self.scroll_offset = 0

    def draw_quest_details(self, surface, quest):
        """
        Draw a popup with detailed information about the selected quest.
        """
        popup_width = 400
        popup_height = 200
        popup_x = (config.WIDTH - popup_width) // 2
        popup_y = (config.HEIGHT - popup_height) // 2

        # Draw semi-transparent popup
        popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        popup.fill((30, 30, 30, 220))  # Dark semi-transparent background
        pygame.draw.rect(popup, config.WHITE, (0, 0, popup_width, popup_height), 2, border_radius=10)
        surface.blit(popup, (popup_x, popup_y))

        # Draw quest title
        title_text = self.large_font.render("Quest Details", True, config.WHITE)
        surface.blit(title_text, (popup_x + 20, popup_y + 20))

        # Draw quest description
        description_text = self.font.render(f"Description: {quest.description}", True, config.WHITE)
        surface.blit(description_text, (popup_x + 20, popup_y + 60))

        # Draw quest objective
        objective_text = self.font.render(f"Objective: {quest.objective}", True, config.WHITE)
        surface.blit(objective_text, (popup_x + 20, popup_y + 90))

        # Draw quest reward
        reward_text = self.font.render(f"Reward: {quest.reward}", True, config.WHITE)
        surface.blit(reward_text, (popup_x + 20, popup_y + 120))

        # Instruction to close popup
        close_text = self.font.render("Press 'Q' to close", True, config.WHITE)
        surface.blit(close_text, (popup_x + popup_width - 150, popup_y + popup_height - 30))

    def draw(self, surface):
        if not self.active:
            return

        # Draw semi-transparent panel with rounded corners
        panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel.fill((50, 50, 50, 200))  # Dark semi-transparent background
        pygame.draw.rect(panel, config.WHITE, panel.get_rect(), 2, border_radius=15)  # White border with rounded corners
        surface.blit(panel, (self.panel_x, self.panel_y))

        # Draw title with shadow for better visibility
        title_shadow = self.large_font.render("Quests", True, config.BLACK)
        title_text = self.large_font.render("Quests", True, config.WHITE)
        surface.blit(title_shadow, (self.panel_x + 15, self.panel_y + 15))
        surface.blit(title_text, (self.panel_x + 10, self.panel_y + 10))

        # Draw search bar
        search_bar_rect = pygame.Rect(self.panel_x + 10, self.panel_y + 40, self.panel_width - 20, 30)
        pygame.draw.rect(surface, config.WHITE, search_bar_rect, 2, border_radius=5)
        search_text = self.font.render(f"Search: {self.search_query}", True, config.WHITE)
        surface.blit(search_text, (self.panel_x + 15, self.panel_y + 45))
        if self.typing:
            pygame.draw.rect(surface, config.YELLOW, search_bar_rect, 2, border_radius=5)  # Highlight when typing

        # Draw Sort By Label
        sort_label = self.font.render("Sort By:", True, config.WHITE)
        surface.blit(sort_label, (self.panel_x + 10, self.panel_y + 80))

        # Draw Sort Option
        sort_option_text = self.option_font.render(self.sort_option, True, config.WHITE)
        sort_option_rect = sort_option_text.get_rect(center=(self.panel_x + 100, self.panel_y + 80))
        pygame.draw.rect(surface, (80, 80, 80), sort_option_rect.inflate(10, 10), border_radius=5)
        surface.blit(sort_option_text, sort_option_rect)

        # Draw Filter By Label
        filter_label = self.font.render("Filter By:", True, config.WHITE)
        surface.blit(filter_label, (self.panel_x + 10, self.panel_y + 120))

        # Draw Filter Option
        filter_option_text = self.option_font.render(self.filter_option, True, config.WHITE)
        filter_option_rect = filter_option_text.get_rect(center=(self.panel_x + 100, self.panel_y + 120))
        pygame.draw.rect(surface, (80, 80, 80), filter_option_rect.inflate(10, 10), border_radius=5)
        surface.blit(filter_option_text, filter_option_rect)

        # Get mouse position relative to the quest panel
        mouse_x, mouse_y = pygame.mouse.get_pos()
        relative_mouse_x = mouse_x - self.panel_x - 10
        relative_mouse_y = mouse_y - self.panel_y - 150 + self.scroll_offset  # Adjusted to match quest list starting y

        # Determine hovered quest index
        hovered_index = (mouse_y - self.panel_y - 150 + self.scroll_offset) // self.quest_height
        if 0 <= hovered_index < len(self.filtered_quests):
            hovered_quest = self.filtered_quests[hovered_index]
        else:
            hovered_quest = None

        # Determine visible quest indices based on scroll_offset
        start_index = self.scroll_offset // self.quest_height
        end_index = start_index + (self.panel_height - 150) // self.quest_height + 1
        visible_quests = self.filtered_quests[start_index:end_index]

        # Draw quests with scroll offset
        for idx, quest in enumerate(visible_quests, start=start_index):
            quest_y = self.panel_y + 150 + (idx - start_index) * self.quest_height - (self.scroll_offset % self.quest_height)
            if quest_y > self.panel_y + self.panel_height:
                break  # No need to draw quests beyond the panel

            if quest_y + self.quest_height < self.panel_y + 150:
                continue  # Skip quests above the visible area

            # Determine if the current quest is hovered
            is_hovered = (hovered_quest == quest)
            if quest == self.selected_quest:
                bg_color = config.YELLOW  # Highlight selected quest
            elif is_hovered:
                bg_color = (100, 100, 100)  # Slightly lighter hover color
            else:
                bg_color = (80, 80, 80)  # Default quest background

            # Draw rounded rectangle for the quest entry
            quest_rect = pygame.Rect(self.panel_x + 10, quest_y, self.panel_width - 20, self.quest_height - 10)
            pygame.draw.rect(surface, bg_color, quest_rect, border_radius=10)

            # Draw quest description
            description_text = self.font.render(quest.description, True, config.WHITE)
            surface.blit(description_text, (self.panel_x + 20, quest_y + 10))

            # Calculate progress ratio
            progress_ratio = quest.progress / quest.target if quest.target else 1

            # Animate progress bar
            target_width = (self.panel_width - 40) * progress_ratio
            current_width = getattr(quest, 'current_progress_width', 0)
            if current_width < target_width:
                quest.current_progress_width = min(current_width + 2, target_width)  # Adjust speed as needed
            elif current_width > target_width:
                quest.current_progress_width = max(current_width - 2, target_width)
            else:
                quest.current_progress_width = target_width

            # Draw the animated filled part
            pygame.draw.rect(surface, config.BLUE, (self.panel_x + 20, quest_y + 35, quest.current_progress_width, 10), border_radius=5)
            pygame.draw.rect(surface, config.WHITE, (self.panel_x + 20, quest_y + 35, self.panel_width - 40, 10), 2, border_radius=5)

            # Draw progress text with shadow
            progress_text = self.font.render(f"{quest.progress}/{quest.target}", True, config.WHITE)
            shadow_text = self.font.render(f"{quest.progress}/{quest.target}", True, (0, 0, 0))
            surface.blit(shadow_text, (
                self.panel_x + 20 + (self.panel_width - 40) / 2 - progress_text.get_width() / 2 + 1,
                quest_y + 35 + 1
            ))
            surface.blit(progress_text, (
                self.panel_x + 20 + (self.panel_width - 40) / 2 - progress_text.get_width() / 2,
                quest_y + 35
            ))

        # Draw scrollbar
        total_height = len(self.filtered_quests) * self.quest_height
        if total_height > self.panel_height - 150:
            scrollbar_height = max((self.panel_height - 150) / total_height * (self.panel_height - 150), 20)
            scrollbar_y = self.panel_y + 150 + (self.scroll_offset / (total_height - (self.panel_height - 150))) * (self.panel_height - 150 - scrollbar_height)
            scrollbar_rect = pygame.Rect(self.panel_x + self.panel_width - 15, scrollbar_y, self.scrollbar_width, scrollbar_height)
            pygame.draw.rect(surface, self.scrollbar_color, (
                self.panel_x + self.panel_width - 15,
                self.panel_y + 150,
                self.scrollbar_width,
                self.panel_height - 150
            ), 2)
            pygame.draw.rect(surface, self.scrollbar_handle_color, scrollbar_rect)

        # Draw quest details popup if a quest is selected
        if self.selected_quest:
            self.draw_quest_details(surface, self.selected_quest)
