PATH=%PATH%;C:\cygwin\bin;
nasm -fobj test.asm -l test.lst
alink\alink.exe -c -oPE -subsys console test
