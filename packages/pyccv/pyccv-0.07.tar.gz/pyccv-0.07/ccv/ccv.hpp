#include <stdlib.h>

extern "C"{
  typedef struct {
    int width;
    int height;
    unsigned char *r;
    unsigned char *g;
    unsigned char *b;
  } rgbimage_t;

  int* calc_ccv(rgbimage_t* img, int blocksize);
  void destructive_reduce_colors(rgbimage_t* img);
  void free_2d_mat(unsigned int** mat,rgbimage_t* img);
  void delete_ptr(int* p);
}
