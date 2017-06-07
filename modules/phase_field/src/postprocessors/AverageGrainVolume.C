/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/

#include "AverageGrainVolume.h"
#include "FeatureFloodCount.h"
#include "MooseMesh.h"
#include "Assembly.h"
#include "MooseVariable.h"

// libMesh includes
#include "libmesh/quadrature.h"

template <>
InputParameters
validParams<AverageGrainVolume>()
{
  InputParameters params = validParams<GeneralPostprocessor>();
  params.addClassDescription("Calculate average grain area in a polycrystal");

  /**
   * This object has two modes of operation: It can be used with the FeatureFloodCount object
   * (recommended) to get the active grain on element information needed to calculate volumes.
   * It can also work on small polycrystals where an equal number of grains and order parameters
   * are used in the simulation. This dual-functionality creates two separate code paths
   * and parameter sets.
   */
  // Mode 1: Use the GrainTracker
  params.addParam<UserObjectName>("feature_counter",
                                  "The FeatureFloodCount UserObject to get values from.");

  // Mode 2: Calculate grain volumes adirectly
  params.addCoupledVarWithAutoBuild(
      "variable", "var_name_base", "op_num", "Array of coupled variables");
  params.addParam<unsigned int>("grain_num", "number of grains to create");
  return params;
}

AverageGrainVolume::AverageGrainVolume(const InputParameters & parameters)
  : GeneralPostprocessor(parameters),
    Coupleable(this, false),
    MooseVariableDependencyInterface(),
    _mesh(_subproblem.mesh()),
    _assembly(_subproblem.assembly(0)),
    _q_point(_assembly.qPoints()),
    _qrule(_assembly.qRule()),
    _JxW(_assembly.JxW()),
    _coord(_assembly.coordTransformation()),
    _feature_counter(isParamValid("feature_counter")
                         ? &getUserObject<FeatureFloodCount>("feature_counter")
                         : nullptr)
{
  if (!_feature_counter)
  {
    if (isParamValid("variable") && isParamValid("grain_num"))
    {
      auto num_coupled_vars = coupledComponents("variable");
      if (num_coupled_vars != getParam<unsigned int>("grain_num"))
        mooseError("The number of grains must match the number of OPs if a feature_counter is not "
                   "supplied");

      _vals.resize(num_coupled_vars);
      for (unsigned int i = 0; i < num_coupled_vars; ++i)
        _vals[i] = &coupledValue("variable", i);

      _feature_volumes.resize(num_coupled_vars);

      // Build a reflexive map (ops map to grains directly)
      _static_var_to_feature.resize(num_coupled_vars);
      for (auto i = beginIndex(_static_var_to_feature); i < num_coupled_vars; ++i)
        _static_var_to_feature[i] = i;
    }
    else
      mooseError("Must supply either a feature_counter object or coupled variables and grain_num");
  }
  else
  {
    const auto & coupled_vars = _feature_counter->getCoupledVars();
    _vals.reserve(coupled_vars.size());

    for (auto & coupled_var : coupled_vars)
      _vals.emplace_back(&coupled_var->sln());

    addMooseVariableDependency(coupled_vars);
  }
}

void
AverageGrainVolume::initialize()
{
  auto num_features = _feature_volumes.size();

  // When using FeatureFloodCount, the number of grains may not be fixed. Resize as appropriate
  if (_feature_counter)
    num_features = _feature_counter->getTotalFeatureCount();

  _feature_volumes.assign(num_features, 0);
}

void
AverageGrainVolume::execute()
{
  auto num_features = _feature_volumes.size();

  const auto end = _mesh.getMesh().active_local_elements_end();
  for (auto el = _mesh.getMesh().active_local_elements_begin(); el != end; ++el)
  {
    const Elem * elem = *el;
    _fe_problem.prepare(elem, 0);
    _fe_problem.reinitElem(elem, 0);

    const std::vector<unsigned int> & var_to_feature_ptr =
        _feature_counter ? _feature_counter->getVarToFeatureVector(elem->id())
                         : _static_var_to_feature;

    accumulateVolumes(var_to_feature_ptr, num_features);
  }
}

void
AverageGrainVolume::accumulateVolumes(const std::vector<unsigned int> & var_to_features,
                                      std::size_t libmesh_dbg_var(num_features))
{
  for (auto var_index = beginIndex(var_to_features); var_index < var_to_features.size();
       ++var_index)
  {
    // Only sample "active" variables
    if (var_to_features[var_index] != FeatureFloodCount::invalid_id)
    {
      auto feature_id = var_to_features[var_index];
      mooseAssert(feature_id < num_features, "Feature ID out of range");
      auto integral_value = computeIntegral(var_index);

      _feature_volumes[feature_id] += integral_value;
    }
  }
}

Real
AverageGrainVolume::computeIntegral(std::size_t var_index) const
{
  Real sum = 0;

  for (unsigned int qp = 0; qp < _qrule->n_points(); ++qp)
    sum += _JxW[qp] * _coord[qp] * (*_vals[var_index])[qp];

  return sum;
}

Real
AverageGrainVolume::getValue()
{
  _communicator.sum(_feature_volumes);

  Real total_volume = 0;
  for (auto & volume : _feature_volumes)
    total_volume += volume;

  return total_volume / _feature_volumes.size();
}