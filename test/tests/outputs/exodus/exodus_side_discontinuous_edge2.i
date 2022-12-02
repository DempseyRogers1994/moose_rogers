[Mesh]
  [square]
    type = GeneratedMeshGenerator
    nx = 16
    dim = 1
  []
[]

[Variables]
  [u]
    order = THIRD
    family = MONOMIAL
  []
  [lambda]
    family = SIDE_HIERARCHIC
    order = CONSTANT
  []
[]

[Kernels]
  [diff]
    type = MatDiffusion
    variable = u
    diffusivity = '1'
  []
  [source]
    type = BodyForce
    variable = u
    value = '1'
  []
[]

[DGKernels]
  [testjumps]
    type = HFEMTestJump
    variable = u
    side_variable = lambda
  []
  [trialjumps]
    type = HFEMTrialJump
    variable = lambda
    interior_variable = u
  []
[]

[BCs]
  [u_robin]
    type = VacuumBC
    boundary = 'left right'
    variable = u
  []
  [lambda_D_unused]
    type = PenaltyDirichletBC
    boundary = 'left right'
    variable = lambda
    penalty = 1
  []
[]

[Postprocessors]
  [intu]
    type = ElementIntegralVariablePostprocessor
    variable = u
    block = 0
  []
  [lambdanorm]
    type = ElementSidesL2Norm
    variable = lambda
  []
[]

[Executioner]
  type = Steady
  solve_type = 'NEWTON'
  petsc_options_iname = '-pc_type -snes_linesearch_type -pc_factor_mat_solver_type'
  petsc_options_value = 'lu       basic                 mumps'
[]

[Outputs]
  [out]
    type = Exodus
    discontinuous = true
    side_discontinuous = true
    file_base = 'exodus_side_discontinuous_edge2_out'
  []
[]
