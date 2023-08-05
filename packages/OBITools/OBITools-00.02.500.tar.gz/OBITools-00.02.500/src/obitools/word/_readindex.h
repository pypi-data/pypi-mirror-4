/*********************************************************************************/
/*********************************************************************************/
/*********************************************************************************/

/*
macros.h:
Binary constant generator macro
By Tom Torfs - donated to the public domain
*/

/* All macro's evaluate to compile-time constants */

/* *** helper macros *** */

/* turn a numeric literal into a hex constant
(avoids problems with leading zeroes)
8-bit constants max value 0x11111111, always fits in unsigned long
*/
#define HEX__(n) 0x##n##LU

/* 8-bit conversion function */
#define B8__(x) ((x&0x0000000FLU)?1:0) \
+((x&0x000000F0LU)?2:0) \
+((x&0x00000F00LU)?4:0) \
+((x&0x0000F000LU)?8:0) \
+((x&0x000F0000LU)?16:0) \
+((x&0x00F00000LU)?32:0) \
+((x&0x0F000000LU)?64:0) \
+((x&0xF0000000LU)?128:0)

/* *** user macros *** */

/* for upto 8-bit binary constants */
#define B8(d) ((unsigned char)B8__(HEX__(d)))

/* for upto 16-bit binary constants, MSB first */
#define B16(dmsb,dlsb) (((unsigned short)B8(dmsb)<< \
+ B8(dlsb))

/* for upto 32-bit binary constants, MSB first */
#define B32(dmsb,db2,db3,dlsb) (((unsigned long)B8(dmsb)<<24) \
+ ((unsigned long)B8(db2)<<16) \
+ ((unsigned long)B8(db3)<< \
+ B8(dlsb))

/*********************************************************************************/
/*********************************************************************************/
/*********************************************************************************/

/*
typedef struct obinuc {
	unsigned int seqused : 1;     // this sequence is already used
	unsigned int endofread : 1;    // this word is already used
	unsigned int zero : 1;        // this is a non standard nucleotide
    unsigned int direction : 1;   // 0 -> use direct word 1 -> use reverse word
    unsigned int reverse    : 2;  // reverse nucleotide 0 : A 1 : C 2 : G 3 : T
    unsigned int forward    : 2;  // forward nucleotide 0 : A 1 : C 2 : G 3 : T
} *pobinuc, obinuc;
*/

typedef char obinuc,*pobinuc;


#define SET_SEQUSED(x)   ((char)((x) | B8(10000000)))
#define SET_ENDOFREAD(x) ((char)((x) | B8(01000000)))
#define SET_ZERO(x)      ((char)((x) | B8(00100000)))
#define SET_DIRECTION(x) ((char)((x) | B8(00010000)))

#define UNSET_SEQUSED(x)   ((char)((x) & B8(01111111)))
#define UNSET_ENDOFREAD(x) ((char)((x) & B8(10111111)))
#define UNSET_ZERO(x)      ((char)((x) & B8(11011111)))
#define UNSET_DIRECTION(x) ((char)((x) & B8(11101111)))


#define SET_REVERSE(x,val)   ((char)(((x) & B8(11110011)) | (((val) & B8(00000011)) << 2)))
#define SET_FORWARD(x,val)   ((char)(((x) & B8(11111100)) | (((val) & B8(00000011)))))

#define GET_SEQUSED(x)   ((char)(((x) >> 7) & 1))
#define GET_ENDOFREAD(x) ((char)(((x) >> 6) & 1))
#define GET_ZERO(x)      ((char)(((x) >> 5) & 1))
#define GET_DIRECTION(x) ((char)(((x) >> 4) & 1))
#define GET_REVERSE(x)   ((char)(((x) >> 2) & B8(00000011)))
#define GET_FORWARD(x)   ((char)(x) & B8(00000011))
#define DECODE_NUC(x)    (*("acgt" + GET_FORWARD(x)))
#define DECODE_NUC_FR(x,d)    (*("acgtn" + (((d==0) ? GET_FORWARD(x):GET_REVERSE(x)) | (GET_ZERO(x) << 2))))

#define A B8(00001100)
#define C B8(00001001)
#define G B8(00000110)
#define T B8(00000011)
#define N B8(00100000)



