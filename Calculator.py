import tkinter as tk
import numpy as np
import tkinter.font as font
from functools import partial
from enum import Enum

class TokenType(Enum):
    BRACKETS = 0
    OPERATOR = 1
    OPERAND = 2


class FormulaToken:
    def __init__(self):
        self.str = None
        self.type = None
        self.reciprocal = False
        self.square = False
        self.negative = False
        self.root = False

    def getValue(self):
        value = float(self.str)
        if self.negative:
            value = value * -1

        if self.square:
            value = value ** 2

        if self.root:
            value = value ** 0.5

        if self.reciprocal:
            value = 1 / value

        return value

    def string(self):
        string = self.str
        if self.negative:
            string = "(-" + string + ")"

        if self.square:
            string = string + "²" 

        if self.root:
            string = "√" + string

        if self.reciprocal:
            string = "(1/" + string + ")" 

        return string

        

class FormulaContainer:
    def __init__(self):
        self.__formula = []

    def __add__(self, character):
        if character == "1/X" or character == "X²" or character == "√X" or character == "±":
            if self.__formula:
                if self.__formula[-1].type == TokenType.OPERAND:
                    if character == "1/X":
                        self.__formula[-1].reciprocal = not self.__formula[-1].reciprocal
                    elif character == "X²":
                        self.__formula[-1].square = not self.__formula[-1].square
                    elif character == "√X":
                        self.__formula[-1].root = not self.__formula[-1].root
                    elif character == "±":
                        self.__formula[-1].negative = not self.__formula[-1].negative
        else:
            if character.isdigit() or character == ".":
                type = TokenType.OPERAND
            elif character == "(" or character == ")":
                type = TokenType.BRACKETS
            else:
                type = TokenType.OPERATOR

            if self.__formula:
                if self.__formula[-1].type == TokenType.OPERAND and type == TokenType.OPERAND:
                    self.__formula[-1].str += character
                elif self.__formula[-1].type == TokenType.OPERATOR and type == TokenType.OPERATOR:
                    self.__formula[-1].str = character
                else:
                    token = FormulaToken()
                    token.str = character
                    token.type = type
                    self.__formula.append(token)
            else:
                token = FormulaToken()
                token.str = character
                token.type = type
                self.__formula.append(token)

        return self

    def eraseLastCharacter(self):
        if self.__formula:
            if self.__formula[-1].type == TokenType.OPERAND and len(self.__formula[-1].str) > 1:
                self.__formula[-1].str = self.__formula[-1].str[:-1:]
            else:
                del self.__formula[-1]

    def getString(self):
        formulaString = ""
        for token in self.__formula:
            formulaString += token.string()

        return formulaString

    def __priority(self, token):
        return 1 if token.str in "+-" else 2 if token.str in "×÷" else 0

    def __postFix(self):
        outputList = []
        stack = []
        for token in self.__formula:
            if token.type == TokenType.OPERAND:
                outputList.append(token)
            else:
                if token.str == "(":
                    stack.append(token)
                elif token.str == ")":
                    while stack[-1].str != "(":
                        outputList.append(stack.pop())

                    stack.pop()
                else:
                    if stack:
                        while self.__priority(stack[-1]) >= self.__priority(token):
                            outputList.append(stack.pop())
                            if not stack:
                                break

                    stack.append(token)

        while stack:
           outputList.append(stack.pop()) 

        return outputList

    def __guess(self):
        token = FormulaToken()
        token.type = TokenType.OPERATOR
        token.str = "×"
        for i in range(len(self.__formula) - 1):
            if self.__formula[i].type == TokenType.OPERAND and self.__formula[i + 1].str == "(":
                self.__formula.insert(i + 1, token)
            elif self.__formula[i + 1].type == TokenType.OPERAND and self.__formula[i].str == ")":
                self.__formula.insert(i + 1, token)
            elif self.__formula[i].str == ")" and self.__formula[i + 1].str == "(":
                self.__formula.insert(i + 1, token)


    def calculate(self):
        if not self.__formula:
            return 0

        self.__guess()
        postFix = self.__postFix()
        stack = []
        for token in postFix:
            if token.type == TokenType.OPERAND:
                stack.append(token.getValue())
            else:
                operand2 = stack.pop()
                operand1 = stack.pop()
                if token.str == "+":
                    result = operand1 + operand2
                elif token.str == "-":
                    result = operand1 - operand2
                elif token.str == "×":
                    result = operand1 * operand2
                elif token.str == "÷":
                    result = operand1 / operand2

                stack.append(result)
        
        answer = stack[0]
        if answer - int(answer) == 0:
            return int(answer)
        else:
            return answer


    def clear(self):
        self.__formula = []


class Core:
    _buttonValue = ["(", ")", "C", "⇦", "1/X", "X²", "√X", "÷", "7", "8", "9", "×", "4", "5", "6", "-", "1", "2", "3", "+", "±", "0", ".", "="]
    _keyboardValue = ["(", ")", "C", "\b", "1/X", "X²", "√X", "/", "7", "8", "9", "*", "4", "5", "6", "-", "1", "2", "3", "+", "±", "0", ".", "\r"]

    def __init__(self):
        self.__formula = FormulaContainer()
        self.errorMessage = False
        self.__answer = 0

    def _setNextCharacter(self, character):
        self.errorMessage = False
        if character == "C":
            self.__formula.clear()
        elif character == "⇦":
            self.__formula.eraseLastCharacter()
        elif character == "=":
            self.errorMessage = True
        else:
            self.__formula += character

    def _getAnswer(self):
        try:
            self.__answer = "=" + str(self.__formula.calculate())
        except:
            if self.errorMessage:
                return "syntax error"

        return self.__answer

    def _getFormula(self):
        return self.__formula.getString()

class GUI(Core):
    def __init__(self):
        super().__init__()
        window = tk.Tk()
        window.resizable(False, False)
        screenWidth = window.winfo_screenwidth()
        screenHeight = window.winfo_screenheight()
        textFormat = font.Font(size = 15, family='Microsoft JhengHei', weight='bold')
        formulaFormat = font.Font(size = 18, family='Microsoft JhengHei', weight='bold')
        answerFormat = font.Font(size = 20, family='Microsoft JhengHei', weight='bold')
        windowWidth = 500
        windowHeight = 700
        window.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, int(screenWidth / 2 - windowWidth / 2), int(screenHeight / 2 - windowHeight / 2)))
        window.title("Super calculator")
        mainPanel = tk.Frame(window, width=windowWidth, height=windowHeight, borderwidth=10, relief="ridge")
        mainPanel.place(x=0, y=0)
        screenPanel = tk.Frame(mainPanel, width=windowWidth-20, height=int((windowHeight - 20) / 3))
        operationPanel = tk.Frame(mainPanel, width=windowWidth-20, height=int((windowHeight - 20)* 2 / 3)-3)
        screenPanel.place(x=0, y=0)
        operationPanel.place(x=0, y=int(windowHeight / 3))
        self.formula = tk.StringVar()
        self.answer = tk.StringVar(value = "=0")
        formulaLabel = tk.Label(screenPanel, textvariable=self.formula, anchor='e', borderwidth=20)
        formulaLabel['font'] = formulaFormat
        answerLabel = tk.Label(screenPanel, textvariable=self.answer, anchor='e', borderwidth=20)
        answerLabel['font'] = answerFormat
        formulaLabel.place(x=0, y=0, width=windowWidth-20, height=int((windowHeight - 20) / 6))
        answerLabel.place(x=0, y=int((windowHeight - 20) / 6), width=windowWidth-20, height=int((windowHeight - 20) / 6))
        index = 0
        for y in range(6):
            for x in range(4):
                button = tk.Button(operationPanel, text=super()._buttonValue[index], activebackground="Gray", bg='snow3')
                button["command"] = partial(self.__buttonListener, button)
                button.place(x=x*int((windowWidth - 20) / 4), y=y*int((windowHeight - 20) / 9), width=int((windowWidth - 20) / 4), height=int((windowHeight - 20) / 9))
                button["font"] = textFormat
                button.bind("<Enter>", partial(self.__enterButton, button))
                button.bind("<Leave>", partial(self.__exitButton, button))
                if button["text"].isdigit() or button["text"] == "." or button["text"] == "±":
                    button['bg'] = 'ghost white'
                elif button["text"] == "=":
                    button['bg'] = 'light sky blue'
                    
                index += 1

        window.bind("<Key>", self.__keyboardListener)
        window.mainloop()

    def __buttonListener(self, button):
        super()._setNextCharacter(button["text"])
        self.__setText()

    def __keyboardListener(self, event):
        try:
            super()._setNextCharacter(super()._buttonValue[super()._keyboardValue.index(event.char.upper())])
            self.__setText()
        except ValueError:
            pass

    def __setText(self):
        self.formula.set(super()._getFormula())
        self.answer.set(super()._getAnswer())
    
    def __enterButton(self, button, event):
        self.currentColor = button['background']
        if self.currentColor == 'light sky blue':
            button['background'] = 'deep sky blue'
        elif self.currentColor == 'ghost white':
            button['background'] = 'gainsboro'
        else:
            button['background'] = 'snow4'

    def __exitButton(self, button, event):
        button['background'] = self.currentColor

class Calculator(GUI):
    def __init__(self):
        super().__init__()


def main():
    Calculator()

if __name__ == '__main__':
    main()
