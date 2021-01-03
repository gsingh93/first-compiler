#===============================================================================
# Compiler Program
# TODO:
# Printing different sizes (wait until data types?)
# Display "text="text
#===============================================================================
import subprocess
import sys

quit = False
Look = ""
LCount = 0;
RawInput = ""
index = 1
lst = []
vars = []
f = open("output","w")

def Input():
	global Look
	global lst
	global RawInput
	global index
	index = 1;
	RawInput = raw_input(">>") #Gets line of input
	RawInput += ';'
	lst = list(RawInput) #Converts each character of RawInput into a list
	Look = lst[0] #Sets Look to the first character of input

def GetChar():
	global Look
	global index
	global lst
	Look = lst[index]
	if(Look != ';'):
		index += 1

def Ident():
	Name = GetName()
	if (Look == '('): # Function
		Match('(')
		Match(')')
		EmitLn("call	" + Name)
	else:
		EmitLn("mov		eax, [" + Name + "]")   #Variable

def Error(s):
	print "Error "+s+"."
	print Look + " Found."
	sys.exit(0)

def Abort(s):
	Error(s)
	#Halt

def Expected(s):
	Abort(s+" Expected")

def Match(x):
	if (Look == x):
		GetChar()
		SkipWhite()
	else:
		Expected(""+x+"")

def IsOp(c):
	return (c == "+" or c == "-" or c == "*" or c == "/" or c == "<" or c == ">" or c == "=")

def IsAddop(c):
	return (c == "+" or c == "-")

def IsMulop(c):
	return (c == "*" or c == "/")

def IsAlpha(c):
	return c.isalpha()

def IsDigit(c):
	return c.isdigit()

def IsAlNum(c):
	return c.isalnum()

def IsWhite(c):
	return (c == " " or c == 9 or c == 10 or c == 13)

def IsBoolean(c):
	return (c.upper() == "T" or c.upper() == "F")

def IsRelop(c):
	return (c.upper() == "=" or c.upper() == "#" or c.upper() == "<" or c.upper() == ">")

def IsOrop(c):
	return (c == "|" or c == "~")

def GetBoolean():
	if (IsBoolean(Look) == False):
		Expected("Boolean Literal")
	returnValue = (Look.upper() == "T")
	GetChar()
	return returnValue

def SkipWhite():
	while(IsWhite(Look)):
		GetChar()

def GetName():
	if(IsAlpha(Look) == False):
		Expected("Name")
	Token = ""
	while(IsAlNum(Look)):
		Token += Look.upper()
		GetChar()
	SkipWhite()
	return Token

#===============================================================================
# def GetName():
#	if(IsAlpha(Look) == False):
#		Expected("Name")
#	Token = Look.upper()
#	GetChar()
#	return Token
#===============================================================================

def NewLabel():
	global LCount
	S = str(LCount)
	LCount += 1
	return 'L' + S
	
def PostLabel(L):
	EmitLn(L + ":")
	
def GetNum():
	if(IsDigit(Look) == False):
		Expected("Integer")
	Value = ""
	while(IsDigit(Look)):
		Value += Look
		GetChar()
	SkipWhite()
	return Value

def Scan():
	if (IsAlpha(Look) == True):
		returnValue = GetName()
	elif (IsDigit(Look) == True):
		returnValue = GetNum()
	elif (IsOp(Look) == True):
		returnValue = GetOp()
	else:
		returnValue = Look
	#GetChar()
	SkipWhite()
	return returnValue

#===============================================================================
# def GetNum():
#	if(IsDigit(Look) == False):
#		Expected("Integer")
#	Value = Look
#	GetChar()
#	return Value
#===============================================================================

def EmitLn(s):
	print s
	f.write(s)
	f.write('\n')
	
def DoIf(L):
	Match('i')
	BoolExpression()
	L1 = NewLabel()
	L2 = L1
	EmitLn("jz	" + L1)
	Block(L)
	if (Look == "l"):
		Match("l")
		L2 = NewLabel()
		EmitLn("jmp		" + L2)
		PostLabel(L1)
		Block(L)
	Match("e")
	PostLabel(L2)
	
def DoWhile():
	Match("w")
	L1 = NewLabel()
	L2 = NewLabel()
	PostLabel(L1)
	BoolExpression()
	EmitLn("jz " + L2)
	Block(L2)
	Match("e")
	EmitLn("jmp " + L1)
	PostLabel(L2)

#Loop, Repeat, for, and do statements can go here

def DoBreak(L):
	Match("b")
	if (L != ""):
		EmitLn("BRA " + L)
	else:
		Abort("No loop to break from")
	
def Other():
	EmitLn(GetName())
	
def Block(L):
	print Look
	while (Look != "e" and Look != "l" and Look != ";"):
		if (Look == "i"):
			DoIf(L)
		elif (Look == "w"): #Loop, repeat, for and do come after this
			DoWhile()
		elif (Look == "b"):
			DoBreak(L)
		else:
			Assignment()
			
def DoProgram():
	Block("")
	if (Look != "e"):
		Expected("END")
	EmitLn("jmp exit") #EMITS END
	
def Equals():
	Match("=")
	Expression()
	EmitLn("pop		ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("sete 	eax") #Assembly may be incorrect
	
def NotEquals():
	Match("#")
	Expression()
	EmitLn("pop 	ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("setne 	eax") #Assembly may be incorrect (might need to be negated)
	
def Less():
	Match("<")
	Expression()
	EmitLn("pop 	ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("setge 	eax") #Assembly may be incorrect
	
def Greater():
	Match(">")
	Expression()
	EmitLn("pop 	ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("setle 	eax") #Assembly may be incorrect

def BoolOr():
	Match("|")
	BoolTerm()
	EmitLn("pop 	ebx")
	EmitLn("or 		eax, ebx")
	
def BoolXor():
	Match("~")
	BoolTerm();
	EmitLn("pop 	ebx")
	EmitLn("xor 	eax, ebx")

def Add():
	Match("+") # Sets Look to the next character
	Term()  # This is called to get the next factor and check for mul/div before add/sub (order of operations)
	EmitLn("pop		ebx")
	EmitLn("add		eax, ebx") # Performs the addition
	
def Subtract():
	Match("-") # Sets Look to the next character
	Term() # This is called to get the next factor and check for mul/div before add/sub (order of operations)
	EmitLn("pop		ebx")
	EmitLn("sub		eax, ebx") # Performs the subtraction
	EmitLn("neg		eax") # Negates the result
	
def Multiply():
	Match("*") # Sets Look to the next character
	Factor() # Gets an expression or moves the number to eax (this is not Term() in order to preserve order of operations)
	EmitLn("pop		ebx")
	EmitLn("imul	eax, ebx") # Performs the multiplication

def Divide():
	Match("/") # Sets Look to the next character
	Factor()  # Gets an expression or moves the number to eax (this is not Term() in order to preserve order of operations)
	EmitLn("xor		edx, edx")
	EmitLn("mov		ebx, eax")
	EmitLn("pop		eax")#exs.l D0
	EmitLn("idiv	ebx") #Performs the division
	
def Relation():
	Expression()
	if IsRelop(Look):
		EmitLn("push 	eax")
		if (Look == "="):
			Equals()
		if (Look == "#"):
			NotEquals()
		if (Look == "<"):
			Less()
		if (Look == ">"):
			Greater()
	EmitLn("test 	eax, 0") #Assembly may be incorrect

def SignedFactor():
	if (Look == "+"):
		GetChar()
	if (Look == "-"):
		GetChar()
		if IsDigit(Look):
			EmitLn("mov		eax, -" + GetNum())
		else:
			Factor()
			EmitLn ("neg 	eax")
	else:
		Factor()

def Factor(): # Either gets an expression or moves a name or number to eax
	if (Look  == "("):
		Match ("(") # If Look = "(", set Look to the next character of Input
		Expression() # This expression is calculted and stored in eax
		Match (")") # If Look = ")", set Look to the next character of Input
	elif (IsAlpha(Look)):
		Ident() # If Look is a character move it to eax. If it is a function call the function. Look is set to the next character
	else:
		EmitLn("mov		eax, " + GetNum()) # If Look is a number, move it to eax. Look is set to the next character

def Term(): # Calls factor to get term then checks for multiplication or addition
	SignedFactor() # Either gets an expression or moves a name or number to eax
	while (IsMulop(Look)): # If the character after the first factor/number is multiplication or division
		EmitLn("push	eax") # Pushes the number moved in Factor()
		if (Look == "*"):
			Multiply()
		elif (Look == "/"):
			Divide()
			
def BoolTerm():
	NotFactor()
	while (Look == "&"):
		EmitLn("push 	eax")
		Match("&")
		NotFactor()
		EmitLn("pop 	ebx")
		EmitLn("and 	eax, ebx")
			
def BoolFactor():
	if (IsBoolean(Look)):
		if (GetBoolean()):
			EmitLn("mov 	eax, -1")
		else:
			EmitLn("clr 	eax")
	else:
		Relation()

def NotFactor():
	if (Look == "!"):
		Match("!")
		BoolFactor()
		EmitLn("xor 	eax, -1")
	else:
		BoolFactor()

def Expression(): # Calls term which calls factor. Checks for addition or subtraction
	Term() 
	while IsAddop(Look): # Addition or subtraction
		EmitLn("push	eax") #Pushes the number moved in Factor()
		if (Look == "+"):
			Add()
		elif (Look == "-"):
			Subtract()
			
def BoolExpression():
	BoolTerm()
	while(IsOrop(Look)):
		EmitLn("push 	eax")
		if (Look == "|"):
			BoolOr()
		if (Look == "~"):
			BoolXor()
			
def Assignment():
	global vars
	Name = GetName()
	Match('=')
	BoolExpression()
	vars.append(Name)
	EmitLn("mov		["+Name+"], eax")
	
def Print(text):
	#String Length Function
#===============================================================================
#	sub	ecx, ecx
#	sub	al, al
#	not	ecx
#	cld
# repne	scasb
#	not	ecx
#	dec	ecx
#===============================================================================
	EmitLn("add		dword [" + text + "], 48")
	
	EmitLn("\n;Write a message to stdout")
	EmitLn("push	dword 0")
	EmitLn("push	dword 0")
	EmitLn("push	dword textlen")
	EmitLn("push	dword " + text)
	EmitLn("push	dword [stdout_handle]")
	EmitLn("call	[WriteFile]")
				
def Init():
	Input() # Gets line of input
	SkipWhite()

EmitLn("[list -]")
EmitLn("%include 'win32n.inc'")
EmitLn("[list +]")

EmitLn("\nsection .bss use32")
EmitLn("section .data use32")
EmitLn("section .code use32")
EmitLn("	cpu 386\n")

EmitLn("extern WriteFile")
EmitLn("extern GetStdHandle")
EmitLn("extern ExitProcess")
EmitLn("import WriteFile kernel32.dll")
EmitLn("import GetStdHandle kernel32.dll")
EmitLn("import ExitProcess kernel32.dll")

EmitLn("\nsection .code\n")
EmitLn("..start:")

EmitLn("push	STD_OUTPUT_HANDLE")
EmitLn("call	[GetStdHandle]			;Get stdout")
EmitLn("mov	 [stdout_handle], eax	  ;Save the handle\n")

#===============================================================================
# while(True):
#	Init() # Gets the first line of input
#	print RawInput
#	if(RawInput.find("quit") != -1):
#		break;
#	DoProgram()
#	RawInput = ""
#	Look = ""
#===============================================================================

Init()
Token = 0;
while(Token != ";"):
	Token = Scan()
	print(Token)


#===============================================================================
# EmitLn("\nexit:")
# Print("Y")
# EmitLn("push	dword 0					;Point at error code")
# EmitLn("call	[ExitProcess]")
#		
# EmitLn("jmp		exit					;Should never reach here")
# 
# EmitLn("\nsection .data\n")
# EmitLn("stdout_handle	dd	0")
# EmitLn("string			dd	0") # How to make this variable length!
# EmitLn("textlen			equ	$ - string")
# 
# vars = list(set(vars))
# for var in vars:
#	EmitLn(var + "			dd 0")
#===============================================================================

#subprocess.Popen("link.bat", shell=True)
