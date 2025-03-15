import time
import random

class Robot:
    def __init__(self, name):
        self.name = name
        self.position = [0, 0]
        self.battery_level = 100   # 100%
        self.direction = 'NORTH'    # Initial direction
        self.obstacles = []
    
    def move(self, distance):
        if self.battery_level <= 0:
            print(f"{self.name} cannot move. Battery level is too low.")
            return
        
        if 'NORTH' == self.direction:
            self.position[1] += distance
        elif 'SOUTH' == self.direction:
            self.position[1] -= distance
        elif 'EAST' == self.direction:
            self.position[0] += distance
        elif 'WEST' == self.direction:
            self.position[0] -= distance
        
        self.battery_level -= distance * 0.1  # battery drain per distance moved
        print(f"{self.name} moved {distance} units to {self.position}. Battery level: {self.battery_level}%")
        
    def turn(self, direction):
        if direction not in ['LEFT', 'RIGHT']:
            print("Invalid turn direction. Please use 'LEFT' or 'RIGHT'.")
            return
        
        directions = ['NORTH', 'EAST', 'SOUTH', 'WEST']
        index = directions.index(self.direction)
        if direction == 'LEFT':
            index = (index - 1) % 4
        else:
            index = (index + 1) % 4
        self.direction = directions[index]
        print(f"{self.name} turned {direction}. Now facing {self.direction}.")
    
    def recharge(self):
        print(f"{self.name} is recharging...")
        self.battery_level = 100
        time.sleep(2)
        print("Recharge complete. Battery level restored to 100%.")
        
    def detect_obstacles(self):
        # Simulate obstacle detection
        if random.random() < 0.3:  # 30% chance of detecting an obstacle
            obstacle_position = [random.randint(-10, 10), random.randint(-10, 10)]
            self.obstacles.append(obstacle_position)
            print(f"Obstacle detected at position {obstacle_position}.")
            return True
        return False

    def navigate(self, distance):
        if self.detect_obstacles():
            print(f"{self.name} cannot proceed due to obstacles.")
            self.avoid_obstacle()
        else:
            self.move(distance)

    def avoid_obstacle(self):
        original_direction = self.direction
        
        print(f"{self.name} is attempting to avoid obstacle.")
        self.turn('LEFT')
        self.move(1)  # Move left for 1 unit to avoid
        self.turn('RIGHT')  # Restore original direction
        print(f"{self.name} avoided obstacle and returned to original path.")
    

def main():
    robot_name = input("Enter the robot's name: ")
    robot = Robot(robot_name)
    
    while True:
        command = input(f"\n{robot.name}, enter command (move <distance>, turn <LEFT/RIGHT>, recharge, exit): ").strip().lower()
        if command.startswith("move"):
            try:
                distance = int(command.split()[1])
                robot.navigate(distance)
            except (IndexError, ValueError):
                print("Invalid command. Use 'move <distance>'.")
        
        elif command.startswith("turn"):
            direction = command.split()[1].upper()
            robot.turn(direction)
        
        elif command == "recharge":
            robot.recharge()
        
        elif command == "exit":
            print("Exiting the robot control program.")
            break
        
        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()