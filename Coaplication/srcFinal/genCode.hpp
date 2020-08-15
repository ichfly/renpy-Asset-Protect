sha256_init(&ctx);
sha256_update(&ctx, datar, 32);
sha256_final(&ctx, buf);

typedef struct {
    int64_t size;
    int64_t offset;
    int64_t flags;
    int64_t pad2;
    unsigned char key[32];
} PICinfo;

int i = 0;
for(i = 0; i < NUMPIC;i++)
{
 if(memcmp (buf, PICID[i], 32) == 0)
 {
    struct AES_ctx ctx;
    uint8_t iv[]  = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f };
    AES_init_ctx_iv(&ctx, datar, iv);
    unsigned char Copy[sizeof(PICinfo)];
    memcpy(Copy,PICDATA[i],sizeof(Copy));
    AES_CBC_decrypt_buffer(&ctx, Copy, sizeof(Copy));
    PICinfo* data = (PICinfo*)Copy;
    fseek( fp, data->offset, SEEK_SET);
    int64_t sizeR = (((data->size + 31) / 32) * 32);
    unsigned char* buffer = (unsigned char*)malloc(sizeR);
    size_t Byteread = fread(buffer, 1, sizeR, fp);

    AES_init_ctx_iv(&ctx, data->key, iv);
    AES_CBC_decrypt_buffer(&ctx, buffer, sizeR);

#ifdef LOG
  fprintf(flog,"Found %i: size %lld offset %lld (sizeR: %lld) Read %lld Flags: %lld\n",i,data->size,data->offset,sizeR,Byteread,data->flags);
  fprintf(flog,"IndexKey:");
  for(i = 0; i < 32;i++)
   fprintf(flog,"%02x ",buf[i]);
  fprintf(flog,"\n");
  fprintf(flog,"DataKey:");
  for(i = 0; i < 32;i++)
   fprintf(flog,"%02x ",data->key[i]);
  fprintf(flog,"\n");
  fflush(flog);
#endif
    unsigned char *ogbuffer = buffer;
    if (data->flags & 0x2) //additional stuff
    {
        sha256_init(&ctx);
        sha256_update(&ctx, data->key, 32);
        while(data->size > 0)
        {
            //get data
            unsigned char cmd = *buffer;
            data->size--;
            buffer++;
            
            size_t cmdSize = strlen(buffer);
            unsigned char* cmdarg = buffer;
            data->size-= cmdSize;
            buffer += cmdSize;
            data->size--;
            buffer++;
            
            unsigned char cmdType = *buffer;
            data->size--;
            buffer++;
            
#ifdef LOG
            fprintf(flog,"Challange: cmd: %02x (%s) cmp: %02x (todo %d)\n",cmd,cmdarg,cmdType,data->size);
            fflush(flog);
#endif
            
            //send to renpy
            unsigned char * res = sendRez(cmdarg, &cmdSize,cmd);
            if(res)
            {
                res = realloc(res, cmdSize + 1);
                res[cmdSize] = 0x00;
                cmdSize++;
#ifdef LOG
                fprintf(flog,"response: %s (%d)\n",res,cmdSize);
                fflush(flog);
#endif
            }
            if(cmdType == 0 && res)
            {
                sha256_update(&ctx, res, cmdSize);
            }
            free(res);
            
        }
        sha256_final(&ctx, datar);
        //restart with new key
        free(ogbuffer);
        
        sha256_init(&ctx);
        sha256_update(&ctx, datar, 32);
        sha256_final(&ctx, buf);
#ifdef LOG
    fprintf(flog,"newreq:");
    for(i = 0; i < 32;i++)
     fprintf(flog,"%02x ",datar[i]);
    fprintf(flog,"\n");
    fflush(flog);
#endif
        i = -1;
        continue;
        
    }
    if (data->flags & 0x1)
    {
        sendRez(buffer, &data->size,0x42);
    }
    else
    {
        sendRez(buffer, &data->size,0x42 | 0x80);  
    }

    free(buffer);
    break;
 }
}
//nothing found send something that dose not work
if (i == NUMPIC)
{
#ifdef LOG
  fprintf(flog,"Not Found!\n");
  fflush(flog);
#endif
 size_t len = 0;
 sendRez(NULL, &len,0x42 | 0x80);
}
#ifdef LOG
fprintf(flog,"\n");
fflush(flog);
#endif