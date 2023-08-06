#include "ccv.hpp"
#include <string.h>
#include <stdlib.h>
#include <vector>
#include <map>

typedef struct {
  unsigned int x;
  unsigned int y;
} coordinate_t;

typedef std::vector<coordinate_t*> coordary;

typedef struct{
  unsigned int id;
  unsigned int color;
  coordary* coords;
} region_t;

typedef std::map<unsigned int,region_t*> regionmap;

unsigned int is_same_color(unsigned int** img, unsigned int** indexes, unsigned int c ,int x, int y,int width, int height);
void merge_region(region_t* from, region_t* to, unsigned int** indexes,regionmap & regions);
void add_to_region(int x,int y, unsigned int** indexes, region_t* region);
unsigned int** reduce_colors(rgbimage_t* img);
void free_2d_mat(unsigned int** mat,rgbimage_t* img);

int* calc_ccv(rgbimage_t* img,int threashold){

  unsigned int** reduced = reduce_colors(img);
  unsigned int** indexes = new unsigned int*[img->width];
  for(int x=0; x<img->width; ++x){
    indexes[x] = new unsigned int[img->height]();
    //memset(indexes[x],0,sizeof(unsigned int)*img->height);
  }
  regionmap regions;
  region_t* reg_a;
  region_t* reg_b;
  unsigned int ids = 1;
  for(int i=0;i<img->height;++i){
    for(int j=0;j<img->width;++j){
      unsigned int c = reduced[j][i];
      unsigned int a = is_same_color(reduced,indexes,c,j,i-1,img->width,img->height);
      unsigned int b = is_same_color(reduced,indexes,c,j-1,i,img->width,img->height);
      if (a>0&&b>0){//aとbの領域両方と同じ色だった場合
        if(a!=b){//aとbが同じ領域ではない場合
          reg_a = regions.find(a)->second;
          reg_b = regions.find(b)->second;
          if (reg_a->coords->size()>reg_b->coords->size()){//領域aの方が大きい場合
            merge_region(reg_b,reg_a,indexes,regions);//bをaにマージ
            add_to_region(j,i,indexes,reg_a);//aに追加
          }else{
            merge_region(reg_a,reg_b,indexes,regions);//aをbにマージ
            add_to_region(j,i,indexes,reg_b);//bに追加
          }
        }else{//aとbが同じ領域だった場合マージ作業を行わずaに追加
          reg_a = regions.find(a)->second;//上
          add_to_region(j,i,indexes,reg_a);
        }
      }else if(a>0){
        reg_a = regions.find(a)->second;//上
        add_to_region(j,i,indexes,reg_a);//aに追加
      }else if(b>0){
        reg_b = regions.find(b)->second;//左
        add_to_region(j,i,indexes,reg_b);//bに追加
      }else{//どちらとも色が違った場合、新しく領域を作成して追加
        region_t* new_region = new region_t;
        new_region->id=ids;
        new_region->color=c;
        coordary* ary = new coordary;
        coordinate_t* coord = new coordinate_t;
        coord->x=j;
        coord->y=i;
        ary->push_back(coord);
        new_region->coords=ary;
        indexes[j][i]=ids;
        regions.insert(std::pair<int,region_t*>(ids,new_region));
        ++ids;
      }
    }
  }
  //ccvベクトルを格納する領域を
  int* ccv = new int[128];
  memset(ccv,0,sizeof(int)*128);
  //領域に対してイテレーションを行う
  for (regionmap::iterator it=regions.begin();it!=regions.end();++it){
    unsigned int color = it->second->color;
    if ((int)it->second->coords->size()>threashold){
      ccv[color*2]+=1;
    }else{
      ccv[color*2+1]+=1;
    }
    delete it->second->coords;//ついでにnewしたvectorをdelete
    delete it->second;
  }
  free_2d_mat(reduced,img);
  free_2d_mat(indexes,img);
  return ccv;
}

void add_to_region(int x,int y, unsigned int** indexes, region_t* region){
  coordinate_t* coord = new coordinate_t;
  coord->x=x;
  coord->y=y;
  region->coords->push_back(coord);
  indexes[x][y]=region->id;
}

void merge_region(region_t* from, region_t* to, unsigned int** indexes,regionmap & regions){
  unsigned int id = to->id;
  for (coordary::iterator it = from->coords->begin(); it != from->coords->end(); ++it){
    indexes[(*it)->x][(*it)->y]=id;//idを塗り替え
    to->coords->push_back(*it);//マージする
  }
  from->coords->clear();
  delete from->coords;
  regionmap::iterator it = regions.find(from->id);
  regions.erase(it);
  delete from;
}

unsigned int is_same_color(unsigned int** img,unsigned int** indexes, unsigned int c ,int x, int y, int width, int height){
  if (0 <= x && 0 <= y && x < width && y < height){//範囲内かどうか
    if (img[x][y]==c){//同じ色ならidを返す
      return indexes[x][y];
    }else{
      return 0;
    }
  }else{
    return 0;
  }
}

unsigned int** reduce_colors(rgbimage_t* img){
  unsigned int** reduced = new unsigned int*[img->width];
  for(int x=0; x<img->width; x++){
    reduced[x] = new unsigned int[img->height]();
  }
  for(int i=0;i<img->height;++i){
    for(int j=0;j<img->width;++j){
      unsigned int r = img->r[i*img->width+j]/64;
      unsigned int g = img->g[i*img->width+j]/64;
      unsigned int b = img->b[i*img->width+j]/64;
      reduced[j][i] = (14*r + 4*g + b);
    }
  }
  return reduced;
}

void free_2d_mat(unsigned int** mat,rgbimage_t* img){
  for(int i = 0;i< img->width;++i){
    delete[] mat[i];
  }
  delete[] mat;
}

void delete_ptr(int* p){
  delete[] p;
}
