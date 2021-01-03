global start
    extern  GetStdHandle@4
    extern  WriteFile@20
    extern  ExitProcess@4
	import WriteFile@20 kernel32.dll
	import GetStdHandle@4 kernel32.dll
	import ExitProcess@4	kernel32.dll

    section .code
..start:
    ; DWORD  bytes;    
    mov     ebp, esp
    sub     esp, 4

    ; hStdOut = GetstdHandle( STD_OUTPUT_HANDLE)
    push    -11
    call    GetStdHandle@4
    mov     ebx, eax    

    ; WriteFile( hstdOut, message, length(message), &bytes, 0);
    push    0
    lea     eax, [ebp-4]
    push    eax
    push    (messageend - message)
    push    message
    push    ebx
    call    WriteFile@20

    ; ExitProcess(0)
    push    0
    call    ExitProcess@4

    ; never here
    hlt
message:
    db      'Hello, World', 10
messageend:
