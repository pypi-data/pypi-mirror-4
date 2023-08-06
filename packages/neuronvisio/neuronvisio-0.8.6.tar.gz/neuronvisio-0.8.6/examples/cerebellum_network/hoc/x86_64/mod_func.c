#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;
modl_reg(){
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");

    fprintf(stderr," GranGolgiSyn.mod");
    fprintf(stderr," GranPurkSyn.mod");
    fprintf(stderr," KConductance.mod");
    fprintf(stderr," MFExtSynInput.mod");
    fprintf(stderr," MFGranSyn.mod");
    fprintf(stderr," NaConductance.mod");
    fprintf(stderr," PassiveCond.mod");
    fprintf(stderr, "\n");
  }
  _GranGolgiSyn_reg();
  _GranPurkSyn_reg();
  _KConductance_reg();
  _MFExtSynInput_reg();
  _MFGranSyn_reg();
  _NaConductance_reg();
  _PassiveCond_reg();
}
