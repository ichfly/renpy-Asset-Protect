# renpy-Asset-Protect

This is a project that protects assets from being extracted easily. It is not a copy protection for the game. It is not a DRM. It may be possible to use it as such but it needs additional work on top of the work already needed to implement it.
Also it also does not prevent the replacement of an asset. Some function where removed also the reason why the prot format is so horrible (it was auto generated) and the names are not changed to random. Another example is the code gen for genCode.hpp.

Idea is that file can only be loaded while playing the game. So you can’t just extract the files without playing the game.

The steps for loading an image.

renpy --name of File--> coapp #The Challenge can only be accessed if the name is known else it cannot be decrypted<br/>
renpy <----Challenge--- coapp #Example get enemyName (should not be guessable by a generic dumper)<br/>
renpy ----response----> coapp #The response is used as a key for the image. The image can only be decrypted if the response is correct<br/>
renpy <-----image------ coapp #The image

Usage:

Setting up CoApp
1. Create prot Files
2. Use the code generator python Generator.py <base Folder of the game> <Folder with prot Files> <glob paths of files to protect>
3. Copy the generated File genData.hpp to srcFinal
4. Compile the CoApp using your preferred compiler for example tcc Ccompiler\tcc.exe srcFinal\test.c srcFinal\aes.c srcFinal\baseDec.c srcFinal\sha256.c

Setup renpy<br/>
5. Copy test.exe and 000.dat to the folder where the starter Executable is located<br/>
6. Put Protecter.rpy into the game folder #if you can you can obfuscate and/or change this Code a little bit also change the coapp if you change keys (dont forget to recompile)<br/>
7. Make sure that in you release package you remove the Files and only load them through 000.dat and the CoApp<br/>
8. Test your Program again as you can't iterate trough Files anymore that causes some functions to break.


Additional easy stuff:

You can change the obfuscation key for the Archives in loader.py in "def index_archives():" around "key = int(l[25:33], 16)"<br/>
Same in the creator tools/archiver.py around "def archive(prefix, files):" "key = random.randint(0, 0x7ffffffe)" or <br/>
launcher/game/archiver.rpy "self.key = 0x42424242" "self.f.write(b"RPA-3.0 %016x %08x\n" % (indexoff, self.key))"

You can also disallow loading not packed files<br/>
renpy/config.py "force_archives = False" <-- set it to True

All the above options are easily bypassed however still better than being dump able without any adaptation.


You can also obfuscate your .rpyc files python code + C code

Additionally obfuscators for python code and C code are available (some of them cost money)

You also may add additional stuff in genCode.hpp such as additional flags that check stuff or decrypt additional code. That checks stuff.

Another thing you can use it for is for bind the saves to a CPU however this also needs work.


Creating prot files:

Prot Files are the challenges and the expected responses that are needed in order to load files<br/>
The structure of the prot Files is the same as in the renpy directory just with .prot added

So the prot file that is used for "img/test/im1.jpg" is "img/test/im1.jpg.prot" if that does not exist than "img/test.prot" than "img.prot" than "default.prot"

The prot file contains a Flag and then a list of challenges and responses<br/>
The Files starts with a Flag (Encry (don’t use Encry it is super slow) or None)

Followed by N challenges and responses:

Each challenge starts with exec or eval or read (or execs/evals/reads if you want to send the challange encrypted (this does not add any security and it is slower so it is not preferred)

exec is for executing python instructions like globals()["nameDRM"] = name<br/>
eval dose an evaluation like (var < 1) or just name to read the name<br/>
read reads a value

This is followed by the actually challenge body like<br/>
globals()["nameDRM"] = name or name

The body is followed by a newline and endofProtCode to indicate the end of the body.<br/>
This is followed by the expected result of the challenge or n.a. if it is not used.
This is followed by Check or DontCheck that says if the response should be used as key for decrypting the files.<br/>

Example (This checks if the name is Player than copies the name to nameDRM and then if nameDRM is Player):


None<br/>
read<br/>
name<br/>
endofProtCode<br/>
Player<br/>
Check<br/>
eval<br/>
name<br/>
endofProtCode<br/>
Player<br/>
Check<br/>
exec<br/>
globals()["nameDRM"] = name<br/>
endofProtCode<br/>
n.a.<br/>
DontCheck<br/>
read<br/>
nameDRM<br/>
endofProtCode<br/>
Player<br/>
Check
