'''
Skeleton Program code for the AQA A Level Paper 1 Summer 2022 examination
this code should be used in conjunction with the Preliminary Material
written by the AQA Programmer Team
developed in the Python 3.9 programming environment
'''

import random

class Breakthrough():
    '''Main breakthrough class'''
    def __init__(self):
        self.__deck = CardCollection("DECK")
        self.__hand = CardCollection("HAND")
        self.__sequence = CardCollection("SEQUENCE")
        self.__discard = CardCollection("DISCARD")
        self.__score = 0
        self.__locks = []
        self.__game_over = False
        self.__currentl_lock = Lock()
        self.__lock_solved = False
        self.__load_locks()

    def play_game(self):
        '''Main driver for the game'''
        if len(self.__locks) > 0:
            self.__setup_game()
            while not self.__game_over:
                self.__lock_solved = False
                while not self.__lock_solved and not self.__game_over:
                    print()
                    print("Current score:", self.__score)
                    print(self.__currentl_lock.GetLockDetails())
                    print(self.__sequence.GetCardDisplay())
                    print(f"Cards remaining in deck: {self.__deck.GetNumberOfCards()}")
                    print(self.__hand.GetCardDisplay())
                    menu_choice = self.__get_choice()
                    if menu_choice == "D":
                        print(self.__discard.GetCardDisplay())
                    elif menu_choice == "U":
                        card_choice = self.__get_card_choice()
                        discard_or_play = self.__get_discard_or_play_choice()
                        if discard_or_play == "D":
                            self.__move_card(self.__hand, self.__discard, self.__hand.GetCardNumberAt(card_choice - 1))
                            self.__get_card_from_deck(card_choice)
                        elif discard_or_play == "P":
                            self.__play_card_to_sequence(card_choice)
                    if self.__currentl_lock.GetLockSolved():
                        self.__lock_solved = True
                        self.__process_lock_solved()
                self.__game_over = self.__check_if_player_has_lost()
        else:
            print("No locks in file.")

    def __process_lock_solved(self):
        self.__score += 10
        print("Lock has been solved.  Your score is now:", self.__score)
        while self.__discard.GetNumberOfCards() > 0:
            self.__move_card(self.__discard, self.__deck, self.__discard.GetCardNumberAt(0))
        self.__deck.Shuffle()
        self.__currentl_lock = self.__get_random_lock()

    def __check_if_player_has_lost(self):
        if self.__deck.GetNumberOfCards() == 0:
            print("You have run out of cards in your deck.  Your final score is:", self.__score)
            return True
        else:
            return False

    def __setup_game(self):
        choice = input("Enter L to load a game from a file, anything else to play a new game:> ").upper()
        if choice == "L":
            if not self.__load_game("game1.txt"):
                self.__game_over = True
        else:
            self.__create_standard_deck()
            self.__deck.Shuffle()
            for _ in range(5):
                self.__move_card(self.__deck, self.__hand, self.__deck.GetCardNumberAt(0))
            self.__add_difficulty_cards_to_deck()
            self.__deck.Shuffle()
            self.__currentl_lock = self.__get_random_lock()

    def __play_card_to_sequence(self, card_choice):
        if self.__sequence.GetNumberOfCards() > 0:
            if self.__hand.GetCardDescriptionAt(card_choice - 1)[0] != self.__sequence.GetCardDescriptionAt(self.__sequence.GetNumberOfCards() - 1)[0]:
                self.__score += self.__move_card(self.__hand, self.__sequence, self.__hand.GetCardNumberAt(card_choice - 1))
                self.__get_card_from_deck(card_choice)
        else:
            self.__score += self.__move_card(self.__hand, self.__sequence, self.__hand.GetCardNumberAt(card_choice - 1))
            self.__get_card_from_deck(card_choice)
        if self.__check_if_lock_challenge_met():
            print()
            print("A challenge on the lock has been met.")
            print()
            self.__score += 5

    def __check_if_lock_challenge_met(self):
        sequence_as_string = ""
        for count in range(self.__sequence.GetNumberOfCards() - 1, max(0, self.__sequence.GetNumberOfCards() - 3) -1, -1):
            if len(sequence_as_string) > 0:
                sequence_as_string = ", " + sequence_as_string
            sequence_as_string = self.__sequence.GetCardDescriptionAt(count) + sequence_as_string
            if self.__currentl_lock.CheckIfConditionMet(sequence_as_string):
                return True
        return False

    def __setup_card_collection_from_game_file(self, line_from_file, card_col):
        if len(line_from_file) > 0:
            split_line = line_from_file.split(",")
            for item in split_line:
                if len(item) == 5:
                    card_number = int(item[4])
                else:
                    card_number = int(item[4:6])
                if item[0: 3] == "Dif":
                    current_card = DifficultyCard(card_number)
                    card_col.AddCard(current_card)
                else:
                    current_card = ToolCard(item[0], item[2], card_number)
                    card_col.AddCard(current_card)

    def __setup_lock(self, line1, line2):
        split_line = line1.split(";")
        for item in split_line:
            conditions = item.split(",")
            self.__currentl_lock.AddChallenge(conditions)
        split_line = line2.split(";")
        for char, count in enumerate(split_line):
            if char == "Y":
                self.__currentl_lock.SetChallengeMet(count, True)

    def __load_game(self, filename):
        try:
            with open(filename, encoding='utf-8-sig') as file:
                line_from_file = file.readline().rstrip()
                self.__score = int(line_from_file)
                line_from_file = file.readline().rstrip()
                ine_from_file2 = file.readline().rstrip()
                self.__setup_lock(line_from_file, ine_from_file2)
                line_from_file = file.readline().rstrip()
                self.__setup_card_collection_from_game_file(line_from_file, self.__hand)
                line_from_file = file.readline().rstrip()
                self.__setup_card_collection_from_game_file(line_from_file, self.__sequence)
                line_from_file = file.readline().rstrip()
                self.__setup_card_collection_from_game_file(line_from_file, self.__discard)
                line_from_file = file.readline().rstrip()
                self.__setup_card_collection_from_game_file(line_from_file, self.__deck)
                return True
        except FileNotFoundError:
            print("File not loaded")
            return False

    def __load_locks(self):
        filename = "locks.txt"
        self.__locks = []
        try:
            with open(filename, encoding="utf-8-sig") as file: 
                line_from_file = file.readline().rstrip()
                while line_from_file != "":
                    challenges = line_from_file.split(";")
                    lock_from_file = Lock()
                    for C in challenges:
                        conditions = C.split(",")
                        lock_from_file.AddChallenge(conditions)
                    self.__locks.append(lock_from_file)
                    line_from_file = file.readline().rstrip()
        except FileNotFoundError:
            print("File not loaded")

    def __get_random_lock(self):
        return self.__locks[random.randint(0, len(self.__locks) - 1)]

    def __get_card_from_deck(self, card_choice):
        if self.__deck.GetNumberOfCards() > 0:
            if self.__deck.GetCardDescriptionAt(0) == "Dif":
                current_card = self.__deck.RemoveCard(self.__deck.GetCardNumberAt(0))
                print()
                print("Difficulty encountered!")
                print(self.__hand.GetCardDisplay())
                print("To deal with this you need to either lose a key ", end='')
                choice = input("(enter 1-5 to specify position of key) or (D)iscard five cards from the deck:> ")
                print()
                self.__discard.AddCard(current_card)
                current_card.Process(self.__deck, self.__discard, self.__hand, self.__sequence, self.__currentl_lock, choice, card_choice)
        while self.__hand.GetNumberOfCards() < 5 and self.__deck.GetNumberOfCards() > 0:
            if self.__deck.GetCardDescriptionAt(0) == "Dif":
                self.__move_card(self.__deck, self.__discard, self.__deck.GetCardNumberAt(0))
                print("A difficulty card was discarded from the deck when refilling the hand.")
            else:
                self.__move_card(self.__deck, self.__hand, self.__deck.GetCardNumberAt(0))
        if self.__deck.GetNumberOfCards() == 0 and self.__hand.GetNumberOfCards() < 5:
            self.__game_over = True

    def __get_card_choice(self):
        choice = None
        while choice is None:
            try:
                choice = int(input("Enter a number between 1 and 5 to specify card to use:> "))
            except TypeError:
                pass
        return choice

    def __get_discard_or_play_choice(self):
        choice = input("(D)iscard or (P)lay?:> ").upper()
        return choice

    def __get_choice(self):
        print()
        return self.__get_discard_or_play_choice()

    def __add_difficulty_cards_to_deck(self):
        for _ in range(5):
            self.__deck.AddCard(DifficultyCard())

    def __create_standard_deck(self):
        for _ in range(5):
            new_card = ToolCard("P", "a")
            self.__deck.AddCard(new_card)
            new_card = ToolCard("P", "b")
            self.__deck.AddCard(new_card)
            new_card = ToolCard("P", "c")
            self.__deck.AddCard(new_card)
        for _ in range(3):
            new_card = ToolCard("F", "a")
            self.__deck.AddCard(new_card)
            new_card = ToolCard("F", "b")
            self.__deck.AddCard(new_card)
            new_card = ToolCard("F", "c")
            self.__deck.AddCard(new_card)
            new_card = ToolCard("K", "a")
            self.__deck.AddCard(new_card)
            new_card = ToolCard("K", "b")
            self.__deck.AddCard(new_card)
            new_card = ToolCard("K", "c")
            self.__deck.AddCard(new_card)

    def __move_card(self, from_collection, to_collection, CardNumber):
        Score = 0
        if from_collection.GetName() == "HAND" and to_collection.GetName() == "SEQUENCE":
            CardToMove = from_collection.RemoveCard(CardNumber)
            if CardToMove is not None:
                to_collection.AddCard(CardToMove)
                Score = CardToMove.GetScore()
        else:
            CardToMove = from_collection.RemoveCard(CardNumber)
            if CardToMove is not None:
                to_collection.AddCard(CardToMove)
        return Score

    def save_game(self):
        filename = input("Enter file name:> ")
        with open(filename, "w", encoding='utf-8-sig') as f:
            f.write(str(self.__score) + "\n")
            f.write(str(self.__game_over) + "\n")

class Challenge():
    def __init__(self):
        self._Met = False
        self._Condition = []

    def GetMet(self):
        return self._Met

    def SetMet(self, NewValue):
        self._Met = NewValue

    def GetCondition(self):
        return self._Condition

    def SetCondition(self, NewCondition):
        self._Condition = NewCondition


class Lock():
    def __init__(self):
        self._Challenges = []

    def AddChallenge(self, Condition):
        C = Challenge()
        C.SetCondition(Condition)
        self._Challenges.append(C)

    def __ConvertConditionToString(self, C):
        ConditionAsString = ""
        for Pos in range(0, len(C) - 1):
            ConditionAsString += C[Pos] + ", "
        ConditionAsString += C[len(C) - 1]
        return ConditionAsString

    def GetLockDetails(self):
        LockDetails = "\n" + "CURRENT LOCK" + "\n" + "------------" + "\n"
        for C in self._Challenges:
            if C.GetMet():
                LockDetails += "Challenge met: "
            else:
                LockDetails += "Not met:       "
            LockDetails += self.__ConvertConditionToString(C.GetCondition()) + "\n"
        LockDetails += "\n"
        return LockDetails

    def GetLockSolved(self):
        for C in self._Challenges:
            if not C.GetMet():
                return False
        return True

    def CheckIfConditionMet(self, Sequence):
        for C in self._Challenges:
            if not C.GetMet() and Sequence == self.__ConvertConditionToString(C.GetCondition()):
                C.SetMet(True)
                return True
        return False

    def SetChallengeMet(self, Pos, Value):
        self._Challenges[Pos].SetMet(Value)

    def GetChallengeMet(self, Pos): 
        return self._Challenges[Pos].GetMet()

    def GetNumberOfChallenges(self): 
        return len(self._Challenges)    

class Card():
    _NextCardNumber = 0

    def __init__(self):
        self._CardNumber = Card._NextCardNumber
        Card._NextCardNumber += 1
        self._Score = 0

    def GetScore(self):
        return self._Score

    def Process(self, Deck, Discard, Hand, Sequence, CurrentLock, choice, Cardchoice):
        pass

    def GetCardNumber(self): 
        return self._CardNumber

    def GetDescription(self):
        if self._CardNumber < 10:
            return " " + str(self._CardNumber)
        else:
            return str(self._CardNumber)

class ToolCard(Card):
    def __init__(self, *args):
        self._ToolType = args[0]   
        self._Kit = args[1]
        if len(args) == 2:
            super(ToolCard, self).__init__()
        elif len(args) == 3:
            self._CardNumber = args[2]
        self.__SetScore()

    def __SetScore(self):
        if self._ToolType == "K":
            self._Score = 3
        elif self._ToolType == "F":
            self._Score = 2
        elif self._ToolType == "P":
            self._Score = 1
  
    def GetDescription(self):
        return self._ToolType + " " + self._Kit

class DifficultyCard(Card):
    def __init__(self, *args):
        self._CardType = "Dif"   
        if len(args) == 0:
            super(DifficultyCard, self).__init__()
        elif len(args) == 1:
            self._CardNumber = args[0]

    def GetDescription(self):
        return self._CardType

    def Process(self, Deck, Discard, Hand, Sequence, CurrentLock, choice, Cardchoice):
        choiceAsInteger = None
        try:
            choiceAsInteger = int(choice)
        except:
            pass
        if choiceAsInteger is not None:
            if choiceAsInteger >= 1 and choiceAsInteger <= 5:
                if choiceAsInteger >= Cardchoice:
                    choiceAsInteger -= 1
                if choiceAsInteger > 0:
                    choiceAsInteger -= 1
                if Hand.GetCardDescriptionAt(choiceAsInteger)[0] == "K":
                    CardToMove = Hand.RemoveCard(Hand.GetCardNumberAt(choiceAsInteger))
                    Discard.AddCard(CardToMove)
                    return
        Count = 0
        while Count < 5 and Deck.GetNumberOfCards() > 0:
            CardToMove = Deck.RemoveCard(Deck.GetCardNumberAt(0))
            Discard.AddCard(CardToMove)
            Count += 1

class CardCollection():
    def __init__(self, N):
        self._Name = N
        self._Cards = []

    def GetName(self):
        return self._Name

    def GetCardNumberAt(self, X):
        return self._Cards[X].GetCardNumber()

    def GetCardDescriptionAt(self, X):
        return self._Cards[X].GetDescription()

    def AddCard(self, C):
        self._Cards.append(C)
 
    def GetNumberOfCards(self): 
        return len(self._Cards)

    def Shuffle(self):
        for Count in range(10000):
            RNo1 = random.randint(0, len(self._Cards) - 1)
            RNo2 = random.randint(0, len(self._Cards) - 1)
            TempCard = self._Cards[RNo1]
            self._Cards[RNo1] = self._Cards[RNo2]
            self._Cards[RNo2] = TempCard

    def RemoveCard(self, CardNumber):
        CardFound = False
        Pos = 0
        while Pos < len(self._Cards) and not CardFound:
            if self._Cards[Pos].GetCardNumber() == CardNumber:
                CardToGet = self._Cards[Pos]
                CardFound = True
                self._Cards.pop(Pos)
            Pos += 1
        return CardToGet

    def __CreateLineOfDashes(self, Size):
        LineOfDashes = ""
        for Count in range(Size):
            LineOfDashes += "------"
        return LineOfDashes

    def GetCardDisplay(self):
        CardDisplay = "\n" + self._Name + ":"
        if len(self._Cards) == 0:
            return CardDisplay + " empty" + "\n" + "\n"
        else:
            CardDisplay += "\n" + "\n"
        LineOfDashes = ""
        CARDS_PER_LINE = 10
        if len(self._Cards) > CARDS_PER_LINE:
            LineOfDashes = self.__CreateLineOfDashes(CARDS_PER_LINE)
        else:
            LineOfDashes = self.__CreateLineOfDashes(len(self._Cards))
        CardDisplay += LineOfDashes + "\n"
        Complete = False
        Pos = 0
        while not Complete:
            CardDisplay += "| " + self._Cards[Pos].GetDescription() + " "
            Pos += 1
            if Pos % CARDS_PER_LINE == 0:
                CardDisplay += "|" + "\n" + LineOfDashes + "\n"
            if Pos == len(self._Cards):
                Complete = True
        if len(self._Cards) % CARDS_PER_LINE > 0:
            CardDisplay += "|" + "\n"
            if len(self._Cards) > CARDS_PER_LINE:
                LineOfDashes = self.__CreateLineOfDashes(len(self._Cards) % CARDS_PER_LINE)
            CardDisplay += LineOfDashes + "\n"
        return CardDisplay

def main():
    this_game = Breakthrough()
    this_game.play_game()
 
if __name__ == "__main__":
    main()
