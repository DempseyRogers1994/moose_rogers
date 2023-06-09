#
# This test demonstrates an InterfaceKernel (InterfaceDiffusionFlux) that can
# replace a pair of integrated DiffusionFluxBC boundary conditions.
#
# The AuxVariable 'diff' shows the difference between the BC and the InterfaceKernel
# approach.
#

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 50
    ny = 50
  []
  [./box1]
    input = gen
    type = SubdomainBoundingBoxGenerator
    block_id = 1
    bottom_left = '0 0 0'
    top_right = '0.51 1 0'
  [../]
  [./box2]
    input = box1
    type = SubdomainBoundingBoxGenerator
    block_id = 2
    bottom_left = '0.49 0 0'
    top_right = '1 1 0'
  [../]
  [./iface_u]
    type = SideSetsBetweenSubdomainsGenerator
    primary_block = 1
    paired_block = 2
    new_boundary = 10
    input = box2
  [../]
  [./iface_v]
    type = SideSetsBetweenSubdomainsGenerator
    primary_block = 2
    paired_block = 1
    new_boundary = 11
    input = iface_u
  [../]
[]

[Variables]
  [./u1]
    block = 1
    [./InitialCondition]
      type = FunctionIC
      function = 'r:=sqrt((x-0.4)^2+(y-0.5)^2);if(r<0.05,5,1)'
    [../]
  [../]
  [./v1]
    block = 2
    [./InitialCondition]
      type = FunctionIC
      function = 'r:=sqrt((x-0.7)^2+(y-0.5)^2);if(r<0.05,5,1)'
    [../]
  [../]
  [./u2]
    block = 1
    [./InitialCondition]
      type = FunctionIC
      function = 'r:=sqrt((x-0.4)^2+(y-0.5)^2);if(r<0.05,5,1)'
    [../]
  [../]
  [./v2]
    block = 2
    [./InitialCondition]
      type = FunctionIC
      function = 'r:=sqrt((x-0.7)^2+(y-0.5)^2);if(r<0.05,5,1)'
    [../]
  [../]
[]

[Kernels]
  [./u1_diff]
    type = Diffusion
    variable = u1
    block = 1
  [../]
  [./u1_dt]
    type = TimeDerivative
    variable = u1
    block = 1
  [../]
  [./v1_diff]
    type = Diffusion
    variable = v1
    block = 2
  [../]
  [./v1_dt]
    type = TimeDerivative
    variable = v1
    block = 2
  [../]

  [./u2_diff]
    type = Diffusion
    variable = u2
    block = 1
  [../]
  [./u2_dt]
    type = TimeDerivative
    variable = u2
    block = 1
  [../]
  [./v2_diff]
    type = Diffusion
    variable = v2
    block = 2
  [../]
  [./v2_dt]
    type = TimeDerivative
    variable = v2
    block = 2
  [../]
[]

[AuxVariables]
  [./diff]
  [../]
[]

[AuxKernels]
  [./u_side]
    type = ParsedAux
    variable = diff
    block = 1
    coupled_variables = 'u1 u2'
    expression = 'u1 - u2'
  [../]
  [./v_side]
    type = ParsedAux
    variable = diff
    block = 2
    coupled_variables = 'v1 v2'
    expression = 'v1 - v2'
  [../]
[]

[InterfaceKernels]
  [./iface]
    type = InterfaceDiffusionBoundaryTerm
    boundary = 10
    variable = u2
    neighbor_var = v2
  [../]
[]

[BCs]
  [./u_boundary_term]
    type = DiffusionFluxBC
    variable = u1
    boundary = 10
  [../]
  [./v_boundary_term]
    type = DiffusionFluxBC
    variable = v1
    boundary = 11
  [../]
[]

[Executioner]
  type = Transient
  dt = 0.001
  num_steps = 20
[]

[Outputs]
  exodus = true
  print_linear_residuals = false
[]
