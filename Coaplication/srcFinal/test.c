#include <stdio.h>
#include <stdlib.h>	// atoi()
#include <stdint.h>
#include "base64.h"
#include <time.h> 
#include "sha256.h"
#include <errno.h>
#include "string.h"
#include "AES.h"
#include <stdbool.h> 

unsigned char updateDRMKey();

#define LOG
//#define LOGKegen

#ifdef LOG
 FILE * flog;
#endif

int getline(char **lineptr, size_t *n, FILE *stream)
{
static char line[256];
char *ptr;
unsigned int len;

   if (lineptr == NULL || n == NULL)
   {
      errno = EINVAL;
      return -1;
   }

   if (ferror (stream))
      return -1;

   if (feof(stream))
      return -1;
     
   fgets(line,256,stream);

   ptr = strchr(line,'\n');   
   if (ptr)
      *ptr = '\0';

   len = strlen(line);
   
   if ((len+1) < 256)
   {
      ptr = realloc(*lineptr, 256);
      if (ptr == NULL)
         return(-1);
      *lineptr = ptr;
      *n = 256;
   }

   strcpy(*lineptr,line); 
   return(len);
}



#include "genData.hpp"

unsigned char SECKEY1[100] = {123, 175, 106, 144, 225, 102, 194, 195, 229, 105, 213, 122, 32, 146, 15, 9, 161, 104, 151, 63, 167, 54, 152, 140, 200, 59, 100, 57, 111, 223, 215, 70, 6, 247, 190, 71, 186, 127, 134, 10, 34, 207, 67, 3, 164, 147, 4, 126, 138, 109, 124, 74, 101, 174, 240, 114, 49, 220, 41, 135, 137, 153, 35, 80, 13, 42, 162, 93, 141, 92, 172, 23, 116, 158, 136, 98, 43, 199, 212, 182, 132, 192, 18, 185, 24, 14, 91, 39, 77, 7, 89, 202, 69, 95, 218, 28, 155, 252, 21, 97};
unsigned char SECKEY2[100] = {196, 208, 139, 228, 134, 191, 6, 144, 193, 2, 65, 241, 125, 106, 189, 145, 24, 104, 73, 98, 171, 225, 109, 214, 101, 175, 229, 143, 141, 33, 107, 182, 105, 152, 131, 41, 22, 162, 70, 77, 129, 30, 165, 126, 207, 151, 50, 136, 21, 49, 137, 237, 75, 133, 56, 68, 220, 44, 185, 91, 172, 180, 192, 179, 83, 118, 132, 92, 29, 17, 215, 155, 209, 99, 60, 149, 5, 45, 43, 79, 115, 1, 255, 238, 87, 20, 217, 248, 232, 168, 121, 199, 111, 161, 123, 253, 78, 67, 72, 117};

void send(unsigned char *data, size_t len,bool encry)
{
 if(encry)
 {
  int i2;
  for(i2 = 0; i2 < len;i2++)
   data[i2] = data[i2] ^ updateDRMKey();
 } 
 size_t output_length;
 unsigned char * dataout = base64_encode(data,
                             len,
                             &output_length);
 fwrite(dataout, output_length, 1, stdout);
 fputs("\n", stdout);
 fflush(stdout);
 free(dataout);
}
unsigned char * recive(size_t* len)
{
  char *line = NULL;
  size_t lineSize = 0;
  lineSize = getline(&line, len, stdin);
  unsigned char * data = base64_decode(line,
                             lineSize,
                             len);
  free(line);
  return data;
}
char* sendRez(unsigned char *data, size_t *len,unsigned char cmd)
{
    unsigned char tempcmd = cmd;
    send(&tempcmd, 1,true);
    send(data, *len,(cmd & 0x80) == 0);
    if((cmd & 0x40) == 0)
    {
        unsigned char * resp = recive(len);
        size_t lend = *len;
        int i;
        for(i = 0; i < lend;i++)
            resp[i] = resp[i] ^ updateDRMKey();
        return resp;
    }
    return NULL;
}
unsigned char DRMKey[100];
unsigned char updateDRMKey()
{
 unsigned char tk = ((DRMKey[0] ^ DRMKey[0x16] ^ DRMKey[0x24] ^ DRMKey[99]) + 0x53) % 255;
 int i;
 for (i = 0;i < 99;i++)
  DRMKey[i] = DRMKey[i + 1];
 DRMKey[99] = tk;
#ifdef LOGKegen
  fprintf(flog,"Key %02x\n",DRMKey[2]);
  fflush(flog);
#endif
 return DRMKey[2];
}
int main(int argc, char **argv) 
{
#ifdef LOG
 flog = fopen ("DRM.log", "w");
#endif

 build_decoding_table();


#ifdef LOG
 fprintf(flog,"Start\n");
 fflush(flog);
#endif


 srand(time(0)); //dose not need to be secure only for obfuscation
 unsigned char key1[100];
 unsigned char key2[100];
 FILE * fp = fopen ("000.dat", "rb");
 for(int i = 0; i<100; i++) 
  key1[i] = (rand() % 0xFF);
 
 unsigned char tosend[100];
 int i;
 for(i = 0; i < 100;i++)
   tosend[i] = key1[i] ^ SECKEY1[i];
 send(tosend,sizeof(tosend),false);
 size_t len = 0;
 for(i = 0; i < 100;i++)
 {
  unsigned char* data = recive(&len);
  key2[i] = data[0] ^ SECKEY2[i];
  free(data);
 }
 for(i = 0; i < 100;i++)
  if (i % 13 == 0)
   DRMKey[i] = key1[i];
  else if (i % 7 == 0)
   DRMKey[i] = key2[i];
  else
   DRMKey[i] = key1[i] ^ key2[i];

#ifdef LOG
 fprintf(flog,"Key1: ");
 for(i = 0; i < 100;i++)
  fprintf(flog,"%u ",key1[i]);
 fprintf(flog,"\nKey2: ");
 for(i = 0; i < 100;i++)
  fprintf(flog,"%u ",key2[i]);
 fprintf(flog,"\nDRMKey: ");
 for(i = 0; i < 100;i++)
  fprintf(flog,"%u ",DRMKey[i]);
 fprintf(flog,"\n");
 fflush(flog);
#endif

 unsigned char buf[SHA256_BLOCK_SIZE];
 SHA256_CTX ctx; //stuff that needs to be more secure

 int64_t count = 0;
 while(1 == 1)
 {
  size_t len = 0;
  unsigned char* datac = recive(&len);
  unsigned char cmd = datac[0] ^ updateDRMKey();
  free(datac);
#ifdef LOG
 fprintf(flog,"cmd:%02x\n",cmd);
 fflush(flog);
#endif

  if(cmd == 0x42)
  {
   unsigned char* datar = recive(&len);
   for(i = 0; i < 32;i++)
    datar[i] = datar[i] ^ updateDRMKey();
#ifdef LOG
    fprintf(flog,"req:");
    for(i = 0; i < 32;i++)
     fprintf(flog,"%02x ",datar[i]);
    fprintf(flog,"\n");
    fflush(flog);
#endif
   #include "genCode.hpp"
   free(datar);
  }
  count++;
 }
 base64_cleanup();
}
