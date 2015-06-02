#ifndef ONEDMOMENTUMFLUX_H
#define ONEDMOMENTUMFLUX_H

#include "Kernel.h"

class OneDMomentumFlux;
class SinglePhaseCommonFluidProperties;

template<>
InputParameters validParams<OneDMomentumFlux>();

/**
 * Momentum flux
 */
class OneDMomentumFlux : public Kernel
{
public:
  OneDMomentumFlux(const std::string & name, InputParameters parameters);
  virtual ~OneDMomentumFlux();

protected:
  virtual Real computeQpResidual();
  virtual Real computeQpJacobian();
  virtual Real computeQpOffDiagJacobian(unsigned int jvar);

  bool _is_liquid;
  Real _sign;
  VariableValue & _alpha;
  VariableValue & _rho;
  VariableValue & _rhou;
  VariableValue & _rhoE;

  VariableValue & _rhoA;
  VariableValue & _rhoEA;

  VariableValue & _u_vel;
  VariableValue & _pressure;
  VariableValue & _area;

  unsigned int _rhoA_var_number;
  unsigned int _rhoEA_var_number;
  bool _has_alpha_A;
  unsigned int _alpha_A_liquid_var_number;
  MaterialProperty<Real> * _dp_dalphaA_liquid;

  const SinglePhaseCommonFluidProperties & _spfp;
};

#endif /* ONEDMOMENTUMFLUX_H */
