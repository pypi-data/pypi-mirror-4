#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;
modl_reg(){
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");

    fprintf(stderr," kd3h5.mod");
    fprintf(stderr," na3h5.mod");
    fprintf(stderr, "\n");
  }
  _kd3h5_reg();
  _na3h5_reg();
}
