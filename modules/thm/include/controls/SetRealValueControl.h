#pragma once

#include "THMControl.h"

class Function;

/**
 * This block reads an input computed by the control logic system and sets a value in a specified
 * component
 */
class SetRealValueControl : public THMControl
{
public:
  SetRealValueControl(const InputParameters & parameters);

  virtual void execute();

protected:
  /// The name of the component that is controlled
  const std::string & _component_name;
  /// The parameter name in the component that is controlled
  const std::string & _param_name;
  /// Control parameter name used internally by MOOSE (the name is generated by THM)
  MooseObjectParameterName _ctrl_param_name;
  /// The value that is written into the component
  const Real & _value;

public:
  static InputParameters validParams();
};
