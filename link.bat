PATH=%PATH%;C:\cygwin\bin;
::nasm -f win32 -o output.o output
::ld output.o -o output.exe
nasm -fobj output -l output.lst
alink\alink.exe -c -oPE -subsys console output
output.exe
