import threading


# Installed in the main packages on the uHandPi it's in common_sdk folder
from common.action_group_controller import ActionGroupController
from common.ros_robot_controller_sdk import Board 

def run_action_group(actNum):
    print(f"Running action group {actNum}")
    threading.Thread(target=agc.runAction, args=(actNum,)).start()

if __name__ == "__main__":
    board = Board()
    agc = ActionGroupController(board)
    run_action_group("17_left_move")