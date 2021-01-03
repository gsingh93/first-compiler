#===============================================================================
# Compiler Program
# TODO:
# Add for loop
# <= and >=
# Printing different sizes (wait until data types?)
# Display "text="text
#===============================================================================
import subprocess
import sys

#Global Variables------------------------------------------------------------------------------ 

KWList = ["IF", "ELSE", "WHILE", "ENDIF", "ENDWHILE", "END"]
KWCode = "xilweee"

Look = ""
LCount = 0;

Token = "";
Value = ""

Index = 1
Lst = []
Vars = []

c = open("code.txt", "r")
f = open("output","w")

#General and Error Functions------------------------------------------------------------------------------ 

def Ident():
	GetName()
	if (Look == '('): # Function
		Match('(')
		Match(')')
		EmitLn("call	" + Value)
	else:
		EmitLn("mov		eax, [" + Value + "]")   #Variable

def Error(s):
	print "Error "+ s +"."
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
		
def MatchString(x):
	if (Value != x):
		Expected(""+x+"")

def EmitLn(s):
	print s
	f.write(s)
	f.write('\n')

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

#Boolean Functions------------------------------------------------------------------------------
 
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

def IsBoolean(c):
	return (c.upper() == "T" or c.upper() == "F")

def IsRelop(c):
	return (c.upper() == "=" or c.upper() == "#" or c.upper() == "<" or c.upper() == ">")

def IsOrop(c):
	return (c == "|" or c == "~")

def IsWhite(c):
	return (c == " " or ord(c) == 9 or ord(c) == 10 or ord(c) == 13)

#Misc------------------------------------------------------------------------------ 

def SkipWhite():
	while(IsWhite(Look) == True):
		GetChar()

def NewLabel():
	global LCount
	S = str(LCount)
	LCount += 1
	return 'L' + S
	
def PostLabel(L):
	EmitLn(L + ":")
		
#Input Functions------------------------------------------------------------------------------ 

def Input():
	global Look
	global Lst
	global Index
	
	Index = 1
	RawInput = raw_input(">>") #Gets line of input
	RawInput += ';'
	Lst = list(RawInput) #Converts each character of RawInput into a list
	Look = Lst[0] #Sets Look to the first character of input

def InputFile():
	global Look
	global Lst
	global Index
	global c
	
	Index = 1
	RawInput = c.readline()
	RawInput += ";"
	Lst = list(RawInput)
	Look = Lst[0]	

def GetInput():
	if (File == "y"):
		InputFile()
	else:
		Input()
	SkipWhite()

def GetChar():
	global Look
	global Index
	global Lst
	
	Look = Lst[Index]
	if(Look != ';'):
		Index += 1

def GetBoolean():
	if (IsBoolean(Look) == False):
		Expected("Boolean Literal")
	returnValue = (Look.upper() == "T")
	GetChar()
	return returnValue

def GetName():
	global Value
	global Token
	if(Look == ";"):
		return
	if(IsAlpha(Look) == False):
		Expected("Name")
	Value = ""
	while(IsAlNum(Look) == True):
		Value += Look.upper()
		GetChar()
	SkipWhite()
	
def GetNum():
	global Value
	global Token
	if(IsDigit(Look) == False):
		Expected("Integer")
	Value = ""
	while(IsDigit(Look) == True):
		Value += Look
		GetChar()
	SkipWhite()
	Token = "#"
	
def GetOp():
	global Value
	global Token
	if (IsOp(Look) == False):
		Expected("Operator")
	Value = ""
	while (IsOp(Look) == True):
		Value += Look
		GetChar()
	if (len(Value) == 1):
		Token = Value[0]
	else:
		Token = "?"

#Control Statements------------------------------------------------------------------------------ 

def DoIf(L):
	BoolExpression()
	L1 = NewLabel()
	L2 = L1
	EmitLn("jz		" + L1)
	Block(L)
	if (Token == "l"):
		L2 = NewLabel()
		EmitLn("jmp		" + L2)
		PostLabel(L1)
		Block(L)
	MatchString("ENDIF")
	PostLabel(L2)

def DoWhile():
	L1 = NewLabel()
	L2 = NewLabel()
	PostLabel(L1)
	BoolExpression()
	EmitLn("jz		" + L2)
	Block(L2)
	#MatchString("ENDWHILE")#Match("e")
	EmitLn("jmp		" + L1)
	PostLabel(L2)

def DoBreak(L):
	Match("b")
	if (L != ""):
		EmitLn("jmp " + L) #"BRA " + L
	else:
		Abort("No loop to break from")

#Relation Functions------------------------------------------------------------------------------ 

def Equals():
	Match("=")
	Expression()
	EmitLn("xor		ecx, ecx")
	EmitLn("pop		ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("sete 	cl") #Assembly may be incorrect
	
def NotEquals():
	Match("#")
	Expression()
	EmitLn("xor		ecx, ecx")
	EmitLn("pop 	ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("setne 	cl") #Assembly may be incorrect (might need to be negated)
	
def Less():
	Match("<")
	Expression()
	EmitLn("xor		ecx, ecx")
	EmitLn("pop 	ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("setge 	cl") #Assembly may be incorrect
	
def Greater():
	Match(">")
	Expression()
	EmitLn("xor		ecx, ecx")
	EmitLn("pop 	ebx")
	EmitLn("cmp 	eax, ebx")
	EmitLn("setle 	cl") #Assembly may be incorrect

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

#Arithmetic Functions------------------------------------------------------------------------------ 

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
				
#Expression Functions------------------------------------------------------------------------------ 
	
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
	EmitLn("cmp 	ecx, 0") #Assembly may be incorrect (test eax)

def SignedFactor():
	s = (Look == "-")
	if (IsAddop(Look) == True):
		GetChar()
		SkipWhite()
	Factor()
	if (s == True):
		EmitLn("neg		eax")

def Factor(): # Either gets an expression or moves a name or number to eax
	if (Look  == "("):
		Match ("(") # If Look = "(", set Look to the next character of Input
		Expression() # This expression is calculted and stored in eax
		Match (")") # If Look = ")", set Look to the next character of Input
	elif (IsAlpha(Look)):
		Ident() # If Look is a character move it to eax. If it is a function call the function. Look is set to the next character
	else:
		GetNum()
		EmitLn("mov		eax, " + Value) # If Look is a number, move it to eax. Look is set to the next character
		
def BoolFactor():
	if (IsBoolean(Look)):
		if (GetBoolean()):
			EmitLn("mov 	eax, -1")
		else:
			EmitLn("clr 	eax")
	else:
		Relation()

def Term1():
	while (IsMulop(Look)): # If the character after the first factor/number is multiplication or division
		EmitLn("push	eax") # Pushes the number moved in Factor()
		if (Look == "*"):
			Multiply()
		elif (Look == "/"):
			Divide()

def Term(): # Calls factor to get term then checks for multiplication or addition
	Factor() # Either gets an expression or moves a name or number to eax
	Term1()
	
def FirstTerm():
	SignedFactor()
	Term1()
			
def BoolTerm():
	NotFactor()
	while (Look == "&"):
		EmitLn("push 	eax")
		Match("&")
		NotFactor()
		EmitLn("pop 	ebx")
		EmitLn("and 	eax, ebx")
			
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
			
#Main Functions-----------------------------------------------------------------------

def Scan():
	global Token
	GetName()
	Token = KWCode[Lookup(KWList, Value, 6)]

def Lookup(T, s, n):
	found = False
	i = n
	while(i > 0 and found == False):
		if (s == T[i-1]):
			found = True
		else:
			i -= 1
	return i

def Assignment():
	global Vars
	Name = Value
	Match("=")
	Expression()
	Vars.append(Name)
	EmitLn("mov		["+Name+"], eax")
		
def Block(L):
	GetInput()
	Scan()
	while (Token != "e" and Token != "l" and Look != ";"):
		if (Token == "i"):
			DoIf(L)
		elif (Token == "w"):
			DoWhile()
		elif (Token == "b"):
			DoBreak(L)
		else:
			Assignment()
		if(Look != ";"):
			Scan()
		if(Look == ";"):
			GetInput()
			Scan()
			
def DoProgram():
	while (Value != "END"):
		Block("")
	MatchString("END")
	Print("X")
	EmitLn("jmp		exit") #EMITS END

#Program------------------------------------------------------------------------------ 

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

File = raw_input("Input from file? (y/n): ")
DoProgram()

EmitLn("\nexit:")
EmitLn("push	dword 0					;Point at error code")
EmitLn("call	[ExitProcess]")
	
EmitLn("jmp		exit					;Should never reach here")

EmitLn("\nsection .data\n")
EmitLn("stdout_handle	dd	0")
EmitLn("string			dd	0") # How to make this variable length!
EmitLn("textlen			equ	$ - string")

Vars = list(set(Vars))
for var in Vars:
	EmitLn(var + "			dd 0")

subprocess.Popen("link.bat", shell=True)
