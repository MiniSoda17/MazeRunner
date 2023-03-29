from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from a3_support import AbstractGrid
from constants import GAME_FILE, TASK
from a2_solution import *
from PIL import Image, ImageTk


class LevelView(AbstractGrid):
    """ A view class that displays the maps along with its entities. """
    def __init__ (self, master, dimensions, size, **kwargs):
        """ Initialises certain elements in LevelView

        Parameters:
            dimensions: The # of rows and columns
            size: The pixel size of the maze
            **kwargs: Arguments to be added for the canvas
        """
        super().__init__(master, dimensions, size, **kwargs)
        
    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], item],
             player_pos: tuple[int, int]) -> None:
        """ Clears everything and draws the tiles and entities.

        Parameters:
            tiles: All the tiles laid out in their positions
            items: All the items on the maze
            player_pos: The position of the player entity
        """
        self.clear()
        items[player_pos] = Player(player_pos)

        for row_number, row in enumerate(tiles):
            for tile_number, tile in enumerate(row):
                
                # Adds cells to LevelView
                cell_position = (row_number, tile_number)
                x_min, y_min, x_max, y_max = self.get_bbox(cell_position)
                self.create_rectangle(x_min, y_min, x_max, y_max,
                                      fill=TILE_COLOURS[tile.get_id()])

                # Adds entities to specific cells
                for item_position in items:
                    if item_position == cell_position:
                        entity = items[item_position]
                        self.create_oval(x_min, y_min, x_max, y_max,
                                         fill=ENTITY_COLOURS[entity.get_id()])
                        self.annotate_position((cell_position), entity.get_id())

        del items[player_pos]
                
        
class StatsView(AbstractGrid):
    """ Displays the players stats and their coins. """
    def __init__(self, master: Union[tk.Tk, tk.Frame], width: int, **kwargs):
        """ Creates a new InventoryView within master.

        Parameters:
            master: Where the stats view will be placed
            width: The width of the stats
            kwargs: Additional arguments for StatsView canvas
        """
        stats_dimensions = (2, 4)
        super().__init__(master,  stats_dimensions, (width, STATS_HEIGHT),
                         **kwargs)
        
    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Creates a diagram to see the player's stats.

        Parameters:
            player_stats: The players hunger, thirst and hp
        """
        hp, hunger, thirst = player_stats
        self.annotate_position((0, 0), "HP")
        self.annotate_position((0, 1), "Hunger")
        self.annotate_position((0, 2), "Thirst")
        self.annotate_position((1, 0), str(hp))
        self.annotate_position((1, 1), str(hunger))
        self.annotate_position((1, 2), str(thirst))
        
    def draw_coins(self, num_coins: int) -> None:
        """ Draws the total coins and it's label in statsView.

        Parameters:
            num_coins: The number of total coins
        """
        self.annotate_position((0, 3), "Coins")
        self.annotate_position((1, 3), str(num_coins))
        
    
class InventoryView(tk.Frame):
    """ A frame that displays all the items in player's inventory. """
    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """ Creates an inventory view under master.

        Parameters:
            master: Where inventory is placed
            **kwargs: All the keyword arguments to be entered.
        """
        super().__init__(master, **kwargs)
        self._master = master
        self._inventoryTitle = tk.Label(self, text="Inventory", font=HEADING_FONT)
        self._inventoryTitle.pack(anchor=tk.N)
        self._callback = None

    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        """ Takes in a string of whatever was clicked.

        Parameters:
            callback: String of item clicked
        """
        self._callback = callback

    def clear(self) -> None:
        """ Clears all widgets in Inventory Frame. """
        self.destroy()
        
    def draw_item(self, name: str, num: int, colour: str) -> None:
        """ Creates and binds a label in inventory frame. 

        Parameters:
            name: String of the item
            num: Quantity of said item
            colour: Background colour of the label
        """
        itemLabel = tk.Label(self, text=str(name) + ": " + str(num), bg=colour,
                             font=TEXT_FONT)
        itemLabel.pack(fill=tk.X)
        itemLabel.bind("<Button-1>", lambda event: self._callback(name))
        
    def draw_inventory(self, inventory: Inventory) -> None:
        """ Draws the entire inventory.

        Parameters:
            inventory: All the items in player's inventory
        """
        #draws  all the items in inventory
        for item_name in inventory.get_items():
            if item_name != 'Coin':
                entity_colour_key = inventory.get_items()[item_name]
                item_count = len(entity_colour_key)
                item_colour = ENTITY_COLOURS[entity_colour_key[0].get_id()]
                self.draw_item(item_name, item_count, item_colour)
            
            
class GraphicalInterface (UserInterface):
    """ Manages overall view of the game and enables event handling. """
    def __init__(self, master: tk.Tk) -> None:
        """ Sets the title and banner with necessary frames

        Parameters:
            master: The window it's going to be displayed in.
        """
        self._master = master
        self._master.title("MazeRunner")
        self._banner = tk.Label(self._master, text="MazeRunner", bg="#C1E1C1",
                                font=BANNER_FONT)
        self._banner.pack(side=tk.TOP, ipadx=220)
        self._middleFrame = tk.Frame(self._master)
        self._middleFrame.pack()
        self._statsFrame = tk.Frame(self._master)
        self._statsFrame.pack()

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """ Creates all the widgets for the game

        Parameters:
            dimensions: # of rows and columns
        """
        stats_width = 800

        if TASK == 2:
            self._imageLevelView = ImageLevelView(self._middleFrame, dimensions,
                                                  (MAZE_WIDTH/1.5, MAZE_WIDTH/1.5))
            self._imageLevelView.pack(side=tk.LEFT)
        else:
            self._levelView = LevelView(self._middleFrame, dimensions,
                                        (MAZE_WIDTH/1.5, MAZE_WIDTH/1.5))
            self._levelView.pack(side=tk.LEFT)

        self._inventoryView = InventoryView(self._middleFrame,
                                            height=MAZE_HEIGHT,
                                            width=INVENTORY_WIDTH)
        self._inventoryView.pack(side=tk.RIGHT, expand=1, fill=tk.BOTH)
        self._statsView = StatsView(self._statsFrame, stats_width, bg=THEME_COLOUR)
        self._statsView.pack(anchor=tk.N)

    def clear_all(self) -> None:
        """ Clears all widgets off master. """
        if TASK == 2:
            self._imageLevelView.destroy()
        else:
            self._levelView.destroy()
        self._statsView.destroy()
        self._inventoryView.destroy()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        """ Sets the dimensions to the new dimensions.

        Parameters:
            dimensions: # of rows and columns for new maze
        """
        self._dimensions = dimensions

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        """ Binds the given keypress to a command.

        command: The function given to be executed
        """
        self._master.bind("<Key>", command)
        
    def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
        """ Removes the clicked item out of player inventory and binds the click
            to it.

        Parameters:
            callback: Another function that should be called
        """
        self._inventoryView.set_click_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        """ Draws the entire inventory.

        Parameters:
            inventory: all items in player's inventory
        """
        self._draw_inventory(inventory)

    def draw(self, maze: Maze, items: dict[tuple[int, int], Item],
             player_position: tuple[int, int], inventory: Inventory,
             player_stats: tuple[int, int, int]) -> None:
        """ Draws any non-coin inventory items and adds a bind.

        Parameters:
            maze: the tiles of the maze
            items: all the entities on the maze with their position
            player_position: the (x,y) coordinates of the player
            inventory: all the items in the player's inventory
            player_stats: the number of hp, hunger and thirst they have.
        """
        self._draw_inventory(inventory)
        self._draw_player_stats(player_stats)
        self._draw_level(maze, items, player_position)

    def _draw_inventory(self, inventory: Inventory) -> None:
        """ Draws inventory in the root window.

        Parameters:
            inventory: all the items in player's inventory
        """
        self._inventoryView.draw_inventory(inventory)

        # Draws the number of coins
        coin_count = 0
        coin = 'Coin'
        if coin in inventory.get_items():
            coin_count = len(inventory.get_items()[coin])
        self._statsView.draw_coins(coin_count)
        
    def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item],
                    player_position: tuple[int, int]) -> None:
        """ Draws the maze for the game with items and the player

        Parameters:
            maze: All the tiles in the maze
            items: All the items on the maze
            player_position: The players position on the maze
        """
        if TASK == 2:
            self._imageLevelView.draw(maze.get_tiles(), items, player_position)
        else:
            self._levelView.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Draws all the current player stats for the game.

        Parameters:
            player_stats: A tuple of players hp, hunger & thirst
        """
        self._statsView.draw_stats(player_stats)


class GraphicalMazeRunner(MazeRunner):
    """ Overriding text interface to create a graphical version """
    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """ Creates a new graphical MazeRunner with a view.

        Parameters:
            game_file: The file of the game that will be run
            root: The window that will house GraphicalMazeRunner
        """
        super().__init__(game_file, UserInterface)
        self._root = root
        self._graphicalInterface = GraphicalInterface(self._root)

        if TASK == 2:
            self._menubar = tk.Menu(self._root)
            self._root.config(menu=self._menubar)
            self._filemenu = tk.Menu(self._menubar)
            self._menubar.add_cascade(label="File", menu=self._filemenu)
            self._filemenu.add_command(label="Save game", command=self.save_game)
            self._filemenu.add_command(label="Load game", command=self.load_game)
            self._filemenu.add_command(label="Restart game",
                                       command=self.restart_game)
            self._filemenu.add_separator()
            self._filemenu.add_command(label="Quit", command=self.quit_game)

            self._items = {}
            self._inventory = Inventory([])
            self._player_stats = None
            self._player_pos = None
            self._dimensions = None
            self._filename = None

            self._controlsFrame = ControlsFrame(self._root)
            self._controlsFrame.pack(ipadx=202)
            self._controlsFrame.create_timer()

    def save_game(self):
        """ Saves the game as a file. """
        game_stats = (str(self._model.get_current_maze().get_tiles()) + "\n" +
                      str(self._model.get_current_items()) + "\n" +
                      str(self._model.get_player_inventory().get_items()) + "\n" +
                      str(self._model.get_player_stats()) + "\n" +
                      str(self._model.get_player().get_position()) + "\n" +
                      str(self._model.get_level().get_dimensions()))

        # Prompts the user to save a file with a name
        self._filename = filedialog.asksaveasfile(defaultextension=".txt",
                                                  filetypes=[("Text file",
                                                              ".txt")])
        if self._filename:
            self._filename.write(game_stats)
            self._filename.close()
    
    def load_game(self):
        """ Loads the game from the text file selected. """
        # Prompts user to load in a saved game
        self._filename = filedialog.askopenfilename()
        if self._filename:
            file = open(self._filename, 'r')
            read = file.readlines()
            tiles, items, inventory, player_stats, player_pos, dimensions = read

            self.convert_items(items)
            self.convert_inventory(inventory)
            self.convert_player_stats(player_stats)
            self.convert_player_pos(player_pos)
            self.convert_dimensions(dimensions)
            self.convert_tiles(tiles)

            self._graphicalInterface.clear_all()
            self._graphicalInterface.create_interface(self._dimensions)
            self._graphicalInterface.bind_keypress(self._handle_keypress)
            self._graphicalInterface.set_inventory_callback(self._apply_item)
            self._graphicalInterface.draw(self._maze, self._items,
                                          self._player_pos, self._inventory,
                                          self._player_stats)

    def convert_player_stats(self, player_stats: str):
        """ Converts the player stats from the text file into
            actual player stats.

        Parameters:
            player_stats: The player stats from the text file
        """
        # Removes all unnecessary string characters
        player_stats = player_stats.strip('(')
        player_stats = player_stats.strip(')\n')
        player_stats = player_stats.split(', ')

        health, hunger, thirst = player_stats
        self._player_stats = (int(health), int(hunger), int(thirst))

    def convert_dimensions(self, dimensions: str):
        """ Converts the dimensions from the text_file to actual
            integer dimensions.

        Parameters:
            dimensions: A string of the dimensions
        """
        dimensions = dimensions.strip('[')
        self._dimensions = [int(dimensions[0]), int(dimensions[3])]
        self._maze = Maze((int(dimensions[0]), int(dimensions[3])))

    def convert_player_pos(self, player_pos: str):
        """ Converts the string of player position into integer versions

        Parameters:
            player_pos: A string version of the player
        """
        player_pos = player_pos.strip('(')
        self._player_pos = (int(player_pos[0]), int(player_pos[3]))

    def convert_tiles(self, tiles: str):
        """ Changes a string of tiles into a Maze class.

        Parameters:
            tiles: A string of all the tiles in the maze
        """
        string_converter = {
            'Wall()': '#',
            'Empty()': 'E',
            'Lava()': 'L',
            'Door()': 'D'
        }

        tiles = tiles.split('],')
        for row in tiles:

            # Removes unnecessary string characters
            row = row.replace('[', '')
            row = row.replace(']', '')
            row = row.split(', ')
            each_row = ''

            # Adds each converted tile to a row
            for tile in row:
                tile = tile.strip('')
                tile = tile.strip()
                tile_class = string_converter[tile]
                each_row += tile_class

            self._maze.add_row(each_row)

    def convert_items(self, items: str):
        """ Converts each string item into an item class.

        Parameters:
            items: All the items on the maze
        """
        if '{}' not in items:
            items = items.split('), ')
            for item in items:
                item = item.split(': ')[1]
                entity_class, position = self.convert_to_class(item)
                self._items[position] = entity_class

    def convert_to_class(self, item) -> tuple[int, int]:
        """ Converts each item string to its corresponding class.

        Parameters:
            item: Each item as a string form
        """
        string_converter = {
            'Coin': Coin,
            'Water': Water,
            'Honey': Honey,
            'Apple': Apple,
            'Potion': Potion
        }

        item = item.split('((')
        entity, position = item
        entity = entity.strip()
        position = position[0], position[3]
        x_pos, y_pos = position
        pos = (int(x_pos), int(y_pos))
        entity_class = string_converter[entity](pos)
        return entity_class, pos

    def convert_inventory(self, inventory):
        """ Adds each string item to an Inventory class.

        Parameters:
            inventory: A string of the items in inventory
        """
        if '{}' not in inventory:
            inventory = inventory.split('], ')

            # Removes all unnecessary string characters
            for items in inventory:
                colon_finder = items.find('[')
                items = items[colon_finder:]
                items = items.strip('[')
                items = items.split('),')

                # Adds each converted string item to an inventory class
                for item in items:
                    entity_class, pos =  self.convert_to_class(item)
                    self._inventory.add_item(entity_class)

    def restart_game(self):
        """ Restarts the whole game, resetting it to the original game_file. """
        self._controlsFrame.reset_timer()
        self._model = Model(GAME_FILE)
        self._graphicalInterface.clear_all()
        self.play()
        
    def quit_game(self):
        ans = messagebox.askokcancel('Verify Exit',
                                     'Are you sure you want to quit?')
        if ans:
            self._root.destroy()

    def _handle_keypress(self, e: tk.Event) -> None:
        """ Handles the player's keypress and checks if player has won game.

        Parameters:
            e: whatever key the user has pressed
        """
        self._graphicalInterface.clear_all()

        # Player has attempted a move
        if e.char in (UP, DOWN, LEFT, RIGHT):
            self._model.move_player(MOVE_DELTAS.get(e.char))

        # Player has won a game
        if self._model.has_won():
            messagebox.showinfo('Exit Menu', WIN_MESSAGE)
            self._root.destroy()
        else:
            self.play()

        # Player has lost the game
        if self._model.has_lost():
            messagebox.showinfo('Exit Menu', LOSS_MESSAGE)    
            self._root.destroy()
        
    def _apply_item(self, item_name: str) -> None:
        """ Applies whatever item was clicked on to the player.

        Parameters:
            item_name: the string of the item clicked
        """
        item = self._model.get_player().get_inventory().remove_item(item_name)
        item.apply(self._model.get_player())
        self._graphicalInterface.clear_all()
        self.play()

    def play(self) -> None:
        """ Runs the whole game and creates all the widgets. """
        level_dimensions = self._model.get_level().get_dimensions()
        self._graphicalInterface.create_interface(level_dimensions)
        self._graphicalInterface.bind_keypress(self._handle_keypress)
        self._graphicalInterface.set_inventory_callback(self._apply_item)
        self._graphicalInterface.draw(self._model.get_current_maze(),
                                      self._model.get_current_items(),
                                      self._model.get_player().get_position(),
                                      self._model.get_player_inventory(),
                                      self._model.get_player_stats())


class ImageLevelView(LevelView):
    """ Extends LevelView by adding images instead of circles. """
    def __init__(self, master, dimensions, size, **kwargs):
        """ Initialises certain elements in ImageLevelView extending on elements
            front LevelView. Keeps track of all the images.

        Parameters:
            dimensions: The # of rows and columns
            size: The pixel size of the maze
        """
        super().__init__(master, dimensions, size, **kwargs)
        self._image_storage = []

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], item],
             player_pos: tuple[int, int]) -> None:
        """ Clears everything and draws the tiles and entities as images.

        Parameters:
            tiles: All the tiles laid out in their positions
            items: All the items on the maze
            player_pos: The position of the player entity
        """
        self.clear()
        items[player_pos] = Player(player_pos)

        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):

                # Adds cells to LevelView
                cell_position = (y,x)
                self._cell_width, self._cell_height = self.get_cell_size()
                mid_point_pos = self.get_midpoint(cell_position)
                self.opening_image(TILE_IMAGES, tile, mid_point_pos)

                # Adds entities to specific cells
                for item_position in items:
                    if item_position == cell_position:
                        self.opening_image(ENTITY_IMAGES, items[item_position],
                                           mid_point_pos)

        del items[player_pos]

    def opening_image(self, IMAGES, cell_entities, mid_point_position):
        """ Creates the images for LevelView.

        Parameters:
            IMAGES: The dictionary that contains the image's filename
            cell_entities: The key of the IMAGES dictionary
            mid_point_position: The midpoint of the image
        """
        file_name = 'images/' + IMAGES[cell_entities.get_id()]
        image = Image.open(file_name).resize((int(self._cell_width),
                                              int(self._cell_height)))
        photo = ImageTk.PhotoImage(image)
        self.create_image(mid_point_position, image=photo)
        self._image_storage.append(photo)


class ControlsFrame(tk.Frame):
    """ Manages the restart button, the new game button and timer. """
    def __init__ (self, master, **kwargs):
        """ Initializes all the buttons in the frame.

        Parameters:
            master: The window that the controls frame will be placed.
            **kwargs: Addition arguments to be added to ControlsFrame.
        """
        super().__init__(master, **kwargs)
        self._master = master
        self._restartGame = tk.Button(self, text='Restart game', font=TEXT_FONT)
        self._restartGame.pack(side=tk.LEFT, expand=1)
        self._newGame = tk.Button(self, text='New game', font=TEXT_FONT)
        self._newGame.pack(side=tk.LEFT, expand=1)
        self._timerFrame = tk.Frame(self)
        self._timerFrame.pack(side=tk.RIGHT, expand=1)
        self._minutes = 0
        self._seconds = 0

    def reset_timer(self):
        """ Restarts the timers. """
        self._seconds = 0
        self._minutes = 0
        self._minutes_seconds.config(text=str(self._minutes) + 'm '
                                     + str(self._seconds) + 's')

    def create_timer(self):
        """ Responsible for creating the Timer. """
        one_second = 1000
        self._timerLabel = tk.Label(self._timerFrame, text='Timer',
                                    font=TEXT_FONT)
        self._timerLabel.pack(side=tk.TOP, expand=1)
        self._minutes_seconds = tk.Label(self._timerFrame, font=TEXT_FONT,
                                         text=str(self._minutes) + 'm '
                                         + str(self._seconds) + 's')
        self._minutes_seconds.pack(side=tk.BOTTOM)
        self._master.after(one_second, self.change_seconds)

    def change_seconds(self):
        """ Resets the seconds to zero once it has reached 60. """
        increments = 1
        max_seconds = 60
        seconds_start = 0

        self._seconds += increments
        if self._seconds == max_seconds:
            self._seconds = seconds_start
            self._minutes += increments
        self.clear_all()
        self.create_timer()

    def clear_all(self):
        """ Destroys the entire timer. """
        self._timerLabel.destroy()
        self._minutes_seconds.destroy()

def play_game(root: tk.Tk):
    """ Instantiates GraphicalMazeRunner and inserts the game file with window.

    Parameters:
        root: The window the entire game will be played on
    """
    GraphicalMazeRunner(GAME_FILE, root).play()

def main():
    """ Runs the whole game. """
    root = tk.Tk()
    app = play_game(root)
    root.mainloop()

if __name__ == '__main__':
    main()

        



        




