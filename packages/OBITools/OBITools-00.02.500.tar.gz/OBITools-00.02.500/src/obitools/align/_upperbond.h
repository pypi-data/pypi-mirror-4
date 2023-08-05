int buildTable(const char *sequence, unsigned char *table, int *count);
int compareTable(unsigned char *t1, int over1, unsigned char* t2,  int over2);
int threshold4(int wordcount,double identity);
int thresholdLCS4(int32_t reflen,int32_t lcs);
int ispossible(int len1, unsigned char *t1, int over1,
		       int len2, unsigned char* t2, int over2,
		       double minimum, int normalized, int large);
