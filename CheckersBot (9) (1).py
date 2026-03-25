import time
import copy
import math
import tkinter as tk

# =====================================================================
# CLASS 1: OtherStuff
# Purpose: Handles utility functions, analytics tracking, formatting,
# and time/space complexity metrics for the end-user reports.
# =====================================================================
class OtherStuff:
    def __init__(self):
        # Tracking cumulative analytics for the whole game
        self.TotalNodesExpanded = 0
        self.TotalPruningDone = 0
        self.TotalTimeTaken = 0.0
        self.GainFromOrdering = 0
    
    def ResetTurnAnalytics(self):
        """Resets the analytics counters at the start of each turn."""
        self.TurnNodesExpanded = 0
        self.TurnPruningDone = 0
        self.TurnStartTime = time.time()
        self.TurnMaxDepth = 0
        self.TurnMaxSpaceDepth = 0      # Space Complexity Metric (O(bm))
        self.TurnPruningDepths = []     # Tracking "when" pruning happens

    def RecordNodeExpansion(self, CurrentDepth):
        """Increments node expansion and tracks maximum recursion depth (Space Complexity)."""
        self.TurnNodesExpanded += 1
        self.TotalNodesExpanded += 1
        if CurrentDepth > self.TurnMaxSpaceDepth:
            self.TurnMaxSpaceDepth = CurrentDepth

    def RecordPruningEvent(self, CurrentDepth):
        """Logs a pruning event and records the depth at which it occurred."""
        self.TurnPruningDone += 1
        self.TotalPruningDone += 1
        self.TurnPruningDepths.append(CurrentDepth)

    def RecordOrderingGain(self, PruneDifference):
        """Records how many extra prunes were achieved strictly due to node ordering."""
        self.GainFromOrdering += PruneDifference

    def PrintTurnAnalytics(self, PlayerName, IsHuman=False):
        """Formats and prints the analytics for the just-completed move."""
        TimeTaken = time.time() - self.TurnStartTime
        self.TotalTimeTaken += TimeTaken
        print(f"--- Analytics for {PlayerName} ---")
        if IsHuman:
            print("Nodes Expanded: 0 (Human Move)")
            print("Pruning Count : 0 (Human Move)")
            print("Space Complex.: O(1) (Human Move)")
        else:
            print(f"Nodes Expanded: {self.TurnNodesExpanded}")
            print(f"Pruning Count : {self.TurnPruningDone}")
            print(f"Space Complex.: Max Recursion Depth Reached: {self.TurnMaxSpaceDepth}")
            if self.TurnPruningDone > 0:
                # Summarize when pruning happened to avoid console spam
                UniqueDepths = sorted(list(set(self.TurnPruningDepths)))
                print(f"Pruning Occurred at Depths: {UniqueDepths}")
            
        print(f"Time Taken    : {TimeTaken:.4f} seconds")
        print(f"Target Plies  : {self.TurnMaxDepth} plies")
        print("---------------------------------")

    def PrintFinalAnalytics(self):
        """Displays cumulative analytics at the end of the game."""
        print("\n=== FINAL CUMULATIVE ANALYTICS ===")
        print(f"Total Nodes Expanded : {self.TotalNodesExpanded}")
        print(f"Total Pruning Done   : {self.TotalPruningDone}")
        print(f"Total Time Taken     : {self.TotalTimeTaken:.4f} seconds")
        print(f"Total Ordering Gain  : {self.GainFromOrdering} extra prunes caught")
        print("==================================\n")


# =====================================================================
# CLASS 2: GameBoard
# Purpose: Computational representation of the state, successor function, 
# multi-jump capture logic, and goal test.
# =====================================================================
class GameBoard:
    def __init__(self):
        # 0: Empty, 1: White Man, 2: White King, 3: Black Man, 4: Black King
        # Human is White (starts first, at bottom). Agent is Black (top).
        self.CurrentState = [
            [0, 3, 0, 3, 0, 3, 0, 3],
            [3, 0, 3, 0, 3, 0, 3, 0],
            [0, 3, 0, 3, 0, 3, 0, 3],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0]
         ]

    def DisplayBoard(self, BoardState):
        """Prints the board beautifully to the console."""
        print("\n    0   1   2   3   4   5   6   7")
        print("  +---+---+---+---+---+---+---+---+")
        for RowIndex in range(8):
            RowString = f"{RowIndex} |"
            for ColIndex in range(8):
                PieceValue = BoardState[RowIndex][ColIndex]
                if PieceValue == 0:   RowString += "   |"
                elif PieceValue == 1: RowString += " w |"
                elif PieceValue == 2: RowString += " W |"
                elif PieceValue == 3: RowString += " b |"
                elif PieceValue == 4: RowString += " B |"
            print(RowString)
            print("  +---+---+---+---+---+---+---+---+")
        print()

    def GoalTest(self, BoardState, IsWhiteTurn):
        """Checks if a player has 0 pieces OR 0 available legal moves."""
        WhiteCount, BlackCount = 0, 0
        for Row in BoardState:
            for Piece in Row:
                if Piece in (1, 2): WhiteCount += 1
                if Piece in (3, 4): BlackCount += 1
        
        if WhiteCount == 0: return "Black Wins (White has no pieces)"
        if BlackCount == 0: return "White Wins (Black has no pieces)"
        
        if len(self.SuccessorFunction(BoardState, IsWhiteTurn)) == 0:
            return "Black Wins (White trapped)" if IsWhiteTurn else "White Wins (Black trapped)"
            
        return "Not Finished"

    def EvaluateState(self, BoardState):
        """Heuristic function for AI: counts pieces, giving more weight to Kings."""
        ScoreValue = 0
        for Row in BoardState:
            for Piece in Row:
                if Piece == 1: ScoreValue -= 1
                elif Piece == 2: ScoreValue -= 3
                elif Piece == 3: ScoreValue += 1
                elif Piece == 4: ScoreValue += 3
        return ScoreValue

    def _get_multi_jumps(self, BoardState, Row, Col, IsWhiteTurn):
        """Recursive helper to find all multi-jump capture chains for a single piece."""
        JumpsFound = []
        IsKing = BoardState[Row][Col] in (2, 4)
        EnemyPieces = (3, 4) if IsWhiteTurn else (1, 2)
        ForwardDir = -1 if IsWhiteTurn else 1
        
        Directions = [(ForwardDir, -1), (ForwardDir, 1)]
        if IsKing: Directions.extend([(-ForwardDir, -1), (-ForwardDir, 1)])

        for DRow, DCol in Directions:
            NewRow, NewCol = Row + DRow, Col + DCol
            JumpRow, JumpCol = Row + 2 * DRow, Col + 2 * DCol
            
            if 0 <= JumpRow < 8 and 0 <= JumpCol < 8:
                if BoardState[NewRow][NewCol] in EnemyPieces and BoardState[JumpRow][JumpCol] == 0:
                    NewState = copy.deepcopy(BoardState)
                    NewState[JumpRow][JumpCol] = NewState[Row][Col]
                    NewState[Row][Col] = 0
                    NewState[NewRow][NewCol] = 0
                    
                    Promoted = False
                    if IsWhiteTurn and JumpRow == 0 and not IsKing:
                        NewState[JumpRow][JumpCol] = 2
                        Promoted = True
                    elif not IsWhiteTurn and JumpRow == 7 and not IsKing:
                        NewState[JumpRow][JumpCol] = 4
                        Promoted = True
                    
                    if Promoted:
                        JumpsFound.append(NewState)
                    else:
                        SubJumps = self._get_multi_jumps(NewState, JumpRow, JumpCol, IsWhiteTurn)
                        if SubJumps:
                            JumpsFound.extend(SubJumps)
                        else:
                            JumpsFound.append(NewState)
        return JumpsFound

    def SuccessorFunction(self, BoardState, IsWhiteTurn):
        """Transition Model: Generates all legal moves, strictly enforcing mandatory jumps."""
        PossibleMoves = []
        PossibleJumps = []
        PlayerPieces = (1, 2) if IsWhiteTurn else (3, 4)
        ForwardDir = -1 if IsWhiteTurn else 1

        for Row in range(8):
            for Col in range(8):
                if BoardState[Row][Col] in PlayerPieces:
                    PieceJumps = self._get_multi_jumps(BoardState, Row, Col, IsWhiteTurn)
                    if PieceJumps:
                        PossibleJumps.extend(PieceJumps)

                    IsKing = BoardState[Row][Col] in (2, 4)
                    Directions = [(ForwardDir, -1), (ForwardDir, 1)]
                    if IsKing: Directions.extend([(-ForwardDir, -1), (-ForwardDir, 1)])
                    
                    for DRow, DCol in Directions:
                        NewRow, NewCol = Row + DRow, Col + DCol
                        if 0 <= NewRow < 8 and 0 <= NewCol < 8 and BoardState[NewRow][NewCol] == 0:
                            NewState = copy.deepcopy(BoardState)
                            NewState[NewRow][NewCol] = NewState[Row][Col]
                            NewState[Row][Col] = 0
                            if (IsWhiteTurn and NewRow == 0) or (not IsWhiteTurn and NewRow == 7):
                                NewState[NewRow][NewCol] = 2 if IsWhiteTurn else 4
                            PossibleMoves.append(NewState)

        if len(PossibleJumps) > 0: return PossibleJumps
        return PossibleMoves


# =====================================================================
# CLASS 3: SearchToolBox
# Purpose: Search algorithms, Time limits, and Analytics isolation.
# =====================================================================
class SearchToolBox:
    def __init__(self, GameBoardRef, OtherStuffRef, MaxSeconds, MaxPlies):
        self.BoardObj = GameBoardRef
        self.StatsObj = OtherStuffRef
        self.TimeLimit = MaxSeconds
        self.DepthLimit = MaxPlies

    def CheckTimeLimit(self):
        """Raises exception to break out of searches if time T is exceeded."""
        if time.time() - self.StatsObj.TurnStartTime >= self.TimeLimit:
            raise TimeoutError("Time limit reached")

    def OrderNodes(self, StateList, IsMaxTurn):
        """Orders states to maximize Alpha-Beta Pruning gain."""
        return sorted(StateList, key=lambda st: self.BoardObj.EvaluateState(st), reverse=IsMaxTurn)

    def MeasureOrderingGain(self, CurrentState):
        """Isolated dry-run to measure extra pruning gain without polluting main stats or clocks."""
        TempStatsOff = OtherStuff()
        TempStatsOn = OtherStuff()
        TempStatsOff.ResetTurnAnalytics()
        TempStatsOn.ResetTurnAnalytics()
        
        TestDepth = min(3, self.DepthLimit)
        TempSearchOff = SearchToolBox(self.BoardObj, TempStatsOff, 999.0, TestDepth)
        TempSearchOn = SearchToolBox(self.BoardObj, TempStatsOn, 999.0, TestDepth)
        
        TempSearchOff.AlphaBetaSearch(CurrentState, TestDepth, -math.inf, math.inf, True, False)
        TempSearchOn.AlphaBetaSearch(CurrentState, TestDepth, -math.inf, math.inf, True, True)
        
        Gain = max(0, TempStatsOn.TurnPruningDone - TempStatsOff.TurnPruningDone)
        self.StatsObj.RecordOrderingGain(Gain)

    def MinimaxSearch(self, BoardState, DepthLimit, IsMaxTurn):
        CurrentDepth = self.DepthLimit - DepthLimit
        self.StatsObj.RecordNodeExpansion(CurrentDepth)
        self.CheckTimeLimit()

        IsWhiteTurnContext = not IsMaxTurn
        if DepthLimit == 0 or self.BoardObj.GoalTest(BoardState, IsWhiteTurnContext) != "Not Finished":
            return self.BoardObj.EvaluateState(BoardState), BoardState

        SuccessorStates = self.BoardObj.SuccessorFunction(BoardState, IsWhiteTurnContext)
        if not SuccessorStates:
            return self.BoardObj.EvaluateState(BoardState), BoardState

        BestState = None
        if IsMaxTurn:
            MaxValue = -math.inf
            for NextState in SuccessorStates:
                Value, _ = self.MinimaxSearch(NextState, DepthLimit - 1, False)
                if Value > MaxValue:
                    MaxValue = Value
                    BestState = NextState
            return MaxValue, BestState
        else:
            MinValue = math.inf
            for NextState in SuccessorStates:
                Value, _ = self.MinimaxSearch(NextState, DepthLimit - 1, True)
                if Value < MinValue:
                    MinValue = Value
                    BestState = NextState
            return MinValue, BestState

    def AlphaBetaSearch(self, BoardState, DepthLimit, AlphaVal, BetaVal, IsMaxTurn, UseOrdering=False):
        CurrentDepth = self.DepthLimit - DepthLimit
        self.StatsObj.RecordNodeExpansion(CurrentDepth)
        self.CheckTimeLimit()

        IsWhiteTurnContext = not IsMaxTurn
        if DepthLimit == 0 or self.BoardObj.GoalTest(BoardState, IsWhiteTurnContext) != "Not Finished":
            return self.BoardObj.EvaluateState(BoardState), BoardState

        SuccessorStates = self.BoardObj.SuccessorFunction(BoardState, IsWhiteTurnContext)
        if not SuccessorStates:
            return self.BoardObj.EvaluateState(BoardState), BoardState

        if UseOrdering:
            SuccessorStates = self.OrderNodes(SuccessorStates, IsMaxTurn)

        BestState = None
        if IsMaxTurn:
            MaxValue = -math.inf
            for NextState in SuccessorStates:
                Value, _ = self.AlphaBetaSearch(NextState, DepthLimit - 1, AlphaVal, BetaVal, False, UseOrdering)
                if Value > MaxValue:
                    MaxValue = Value
                    BestState = NextState
                AlphaVal = max(AlphaVal, Value)
                if BetaVal <= AlphaVal:
                    self.StatsObj.RecordPruningEvent(CurrentDepth)
                    break
            return MaxValue, BestState
        else:
            MinValue = math.inf
            for NextState in SuccessorStates:
                Value, _ = self.AlphaBetaSearch(NextState, DepthLimit - 1, AlphaVal, BetaVal, True, UseOrdering)
                if Value < MinValue:
                    MinValue = Value
                    BestState = NextState
                BetaVal = min(BetaVal, Value)
                if BetaVal <= AlphaVal:
                    self.StatsObj.RecordPruningEvent(CurrentDepth)
                    break
            return MinValue, BestState

    def GetBestMove(self, CurrentState, SearchStrategy):
        """Entry point for calculating Agent's move. Handles timeouts gracefully."""
        self.StatsObj.ResetTurnAnalytics()
        self.StatsObj.TurnMaxDepth = self.DepthLimit
        
        if SearchStrategy == "3":
            self.MeasureOrderingGain(CurrentState)
            
        BestNextState = None
        BestValue = -math.inf
        
        SuccessorStates = self.BoardObj.SuccessorFunction(CurrentState, False)
        if not SuccessorStates: return None

        if SearchStrategy == "3":
            SuccessorStates = self.OrderNodes(SuccessorStates, True)

        try:
            for NextState in SuccessorStates:
                if SearchStrategy == "1":
                    Value, _ = self.MinimaxSearch(NextState, self.DepthLimit - 1, False)
                else:
                    Value, _ = self.AlphaBetaSearch(NextState, self.DepthLimit - 1, -math.inf, math.inf, False, SearchStrategy == "3")
                
                if Value > BestValue or BestNextState is None:
                    BestValue = Value
                    BestNextState = NextState
                    
        except TimeoutError:
            print(f"Time limit (T={self.TimeLimit}s) reached! Falling back to best evaluated node so far.")
            
        if BestNextState is None and len(SuccessorStates) > 0:
            BestNextState = SuccessorStates[0]

        return BestNextState


# =====================================================================
# CLASS 4: PlayingTheGame
# Purpose: Manages game flow, strict UX constraints, and UI interactions.
# =====================================================================
class PlayingTheGame:
    def __init__(self):
        self.BoardEngine = GameBoard()
        self.Analytics = OtherStuff()
        self.SearchEngine = None
        self.SearchAlgorithm = "3"
        
    def StartingMoveLocation(self, X, Y): return (X, Y)
    def TargetingMoveLocation(self, X, Y): return (X, Y)

    def SetupEnvironment(self):
        """Contracts constraints from the user, ensuring rigorous limits."""
        print("Welcome to Checkers-Agent AI Game!")
        while True:
            print("Select Search Strategy (S): 1. Minimax | 2. Alpha-Beta | 3. Alpha-Beta w/ Ordering")
            self.SearchAlgorithm = input("Enter 1, 2, or 3: ")
            if self.SearchAlgorithm in ["1", "2", "3"]: break
        
        while True:
            try:
                TimeLimitInput = int(input("Enter Time limit in seconds (T) [1 to 3]: "))
                if 1 <= TimeLimitInput <= 3: break
                print("Error: T must be between 1 and 3 inclusive.")
            except ValueError: pass

        while True:
            try:
                PliesLimitInput = int(input("Enter Look-forward plies (P) [5 to 9]: "))
                if 5 <= PliesLimitInput <= 9: break
                print("Error: P must be between 5 and 9 inclusive.")
            except ValueError: pass

        self.SearchEngine = SearchToolBox(self.BoardEngine, self.Analytics, TimeLimitInput, PliesLimitInput)

    def ApplyHumanMove(self):
        """Processes user input, verifying ownership, targets, and mandatory jumps."""
        ValidStates = self.BoardEngine.SuccessorFunction(self.BoardEngine.CurrentState, True)
        if not ValidStates: return False

        BlackCountBefore = sum(1 for row in self.BoardEngine.CurrentState for p in row if p in (3, 4))
        BlackCountAfter = sum(1 for row in ValidStates[0] for p in row if p in (3, 4))
        JumpForced = BlackCountAfter < BlackCountBefore

        self.Analytics.ResetTurnAnalytics() 
        MoveIsValid = False
        while not MoveIsValid:
            try:
                if JumpForced:
                    print("\n[!] MANDATORY JUMP RULE ACTIVE: You have a forced capture available.")
                    print("You MUST take the jump (For multi-jumps, enter the FINAL Target Line/Column).")
                else:
                    print("\nEnter your move.")
                    
                StartX = int(input("Line of piece to move: "))
                StartY = int(input("Column of piece to move: "))
                StartLoc = self.StartingMoveLocation(StartX, StartY)

                TargetX = int(input("Target Line: "))
                TargetY = int(input("Target Column: "))
                TargetLoc = self.TargetingMoveLocation(TargetX, TargetY)

                if self.BoardEngine.CurrentState[StartLoc[0]][StartLoc[1]] not in (1, 2):
                    print("Invalid start! You must select one of your own White pieces (w or W).")
                    continue
                    
                if self.BoardEngine.CurrentState[TargetLoc[0]][TargetLoc[1]] != 0:
                    print("Invalid target! The destination square must be empty.")
                    continue

                MatchedState = None
                for VState in ValidStates:
                    if VState[StartLoc[0]][StartLoc[1]] == 0 and VState[TargetLoc[0]][TargetLoc[1]] != 0:
                        MatchedState = VState
                        break
                
                if MatchedState is not None:
                    self.BoardEngine.CurrentState = MatchedState
                    MoveIsValid = True
                else:
                    print("Invalid move! Please check your coordinates or available forced jumps.")
            except (ValueError, IndexError): 
                print("Please enter valid integers within board limits (0-7).")
        
        self.Analytics.PrintTurnAnalytics("Human Player (White)", IsHuman=True)
        return True

    def StartGame(self):
        """Main Interactive Game Execution Loop."""
        self.SetupEnvironment()
        if input("Run with GUI (y/n)? ").lower() == 'y':
            import threading
            threading.Thread(target=self.LaunchVisualInterface, daemon=True).start()
        
        self.BoardEngine.DisplayBoard(self.BoardEngine.CurrentState)

        while True:
            GoalStatus = self.BoardEngine.GoalTest(self.BoardEngine.CurrentState, True)
            if GoalStatus != "Not Finished":
                print(f"GAME OVER! {GoalStatus}")
                break

            # 1. Human Turn (White)
            print("--- HUMAN TURN (WHITE) ---")
            HasMoves = self.ApplyHumanMove()
            self.BoardEngine.DisplayBoard(self.BoardEngine.CurrentState)

            # --- BUG FIX: Check Goal status correctly after human move ---
            StatusAfterHuman = self.BoardEngine.GoalTest(self.BoardEngine.CurrentState, False)
            if not HasMoves:
                print("GAME OVER! Black Wins (White trapped)")
                break
            if StatusAfterHuman != "Not Finished":
                print(f"GAME OVER! {StatusAfterHuman}")
                break

            # 2. Agent Turn (Black)
            print("--- AGENT TURN (BLACK) ---")
            AgentMove = self.SearchEngine.GetBestMove(self.BoardEngine.CurrentState, self.SearchAlgorithm)
            
            if AgentMove is None:
                print("GAME OVER! White Wins")
                break
                
            self.BoardEngine.CurrentState = AgentMove
            self.Analytics.PrintTurnAnalytics("Agent Bot (Black)")
            self.BoardEngine.DisplayBoard(self.BoardEngine.CurrentState)

        self.Analytics.PrintFinalAnalytics()

    def LaunchVisualInterface(self):
        """Bonus: A simple Tkinter grid to visualize the board."""
        root = tk.Tk()
        root.title("Checkers Bot GUI")
        labels = [[tk.Label(root, width=4, height=2, relief="raised") for _ in range(8)] for _ in range(8)]
        for r in range(8):
            for c in range(8): labels[r][c].grid(row=r, column=c)
        
        def refresh():
            for r in range(8):
                for c in range(8):
                    val = self.BoardEngine.CurrentState[r][c]
                    chars = {0: "", 1: "w", 2: "W", 3: "b", 4: "B"}
                    labels[r][c].config(text=chars.get(val, ""), bg="black" if (r+c)%2 else "white", fg="white")
            root.after(500, refresh)
        
        refresh()
        root.mainloop()

if __name__ == "__main__":
    GameProcess = PlayingTheGame()
    GameProcess.StartGame()