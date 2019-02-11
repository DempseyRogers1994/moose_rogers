#ifndef PIPEBASE_H
#define PIPEBASE_H

#include "GeometricalFlowComponent.h"

class PipeBase;

template <>
InputParameters validParams<PipeBase>();

/**
 * A base class for pipe components
 *
 * A pipe is defined by its position, direction, length and area.
 * Mesh: mesh is generated in such a way, that the pipe starts at the origin (0, 0, 0) and is
 * aligned with x-axis. Its
 * subdivided into _n_elems elements (of type EDGE2).
 */
class PipeBase : public GeometricalFlowComponent
{
public:
  PipeBase(const InputParameters & params);

  // Pipe specific interface ----
  virtual std::shared_ptr<const FlowModel> getFlowModel() const;
  virtual unsigned int getSubdomainID() const = 0;
  virtual bool isHorizontal() const = 0;

  /**
   * Get the name of the function describing the flow channel area
   *
   * @return The name of the function describing the flow channel area
   */
  const FunctionName & getAreaFunctionName() const { return _area_function; }

protected:
  virtual std::shared_ptr<FlowModel> buildFlowModel();
  virtual void init() override;

  /// The flow model used by this pipe
  std::shared_ptr<FlowModel> _flow_model;

  /// Function describing the flow channel area
  const FunctionName & _area_function;
};

#endif /* PIPEBASE_H */
