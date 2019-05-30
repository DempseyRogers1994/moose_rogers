#ifndef MMSTESTFUNC_H
#define MMSTESTFUNC_H

#include "Function.h"
#include "FunctionInterface.h"

class MMSTestFunc;

template <>
InputParameters validParams<MMSTestFunc>();

/**
 *  Function of RHS for manufactured solution in spatial_constant_helmholtz test
 */
class MMSTestFunc : public Function, public FunctionInterface
{
public:
  MMSTestFunc(const InputParameters & parameters);

  virtual Real value(Real t, const Point & p) override;

protected:
  Real _L;

  const Function & _a;
  const Function & _b;

  Real _d;
  Real _h;

  Real _g0_real;
  Real _g0_imag;

  Real _gL_real;
  Real _gL_imag;

  MooseEnum _component;

};

#endif // MMSTESTFUNC_H
