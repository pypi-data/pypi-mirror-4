#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>
#include "mt64mp.h"
  
  

int main(void)
{
  int ThreadID, NoofThreads; 
  UL64  *  mt , * * mtarr  ;
  UL64 seed = time(NULL) ;
  UL64 * seedarr ; 
  int mti , * mtiarr ;
  int i;

  NoofThreads =  omp_get_max_threads() ;
  mt = newmt ();
  init_genrand64(seed , mt,&mti);

  printf("10 outputs of genrand64_int64()\n");
  for (i=0; i<10; i++) {
    printf("%20llu \n", genrand64_int64(mt,&mti));
  }

  mtarr = (UL64 *  *)malloc((size_t) ((NoofThreads)*sizeof(UL64 *)));
  seedarr = (UL64  *)malloc((size_t) ((NoofThreads)*sizeof(UL64)));
  mtiarr  = (int  * )malloc((size_t) ((NoofThreads)*sizeof(int)));

  printf("Number of Threads #%d\n",NoofThreads) ; 
  // we associate a seed to each  thread
  for (i=0; i<NoofThreads; i++) {
    seedarr[i] = genrand64_int64(mt,&mti) ;
    printf("Sead associated with thread #%d :  %20llu \n", i  ,seedarr[i] );
 }
  

  #pragma omp parallel private(ThreadID)
    {
      ThreadID = omp_get_thread_num();
      printf("Hello from OpenMP Thread #%d!\n",ThreadID);
      mtarr[ThreadID] = newmt ();

      init_genrand64(seedarr[ThreadID] ,mtarr[ThreadID], & mtiarr[ThreadID]  ) ;
      printf("Trhead #%d generates :  %20llu \n",ThreadID ,  genrand64_int64(mtarr[ThreadID], & mtiarr[ThreadID]));

      freemt(mtarr[ThreadID]) ; 

   }
    free(mtarr);
    free(seedarr);
    free(mtiarr);
    freemt(mt) ;

    return 0 ;

}
