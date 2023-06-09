#mms_sine_posprocessor_test.i
#This is for u = sin(a*x*y*z*t)
[Mesh]
  type = GeneratedMesh
  dim = 3
  nx = 4
  ny = 4
  nz = 4
  xmin = 0
  xmax = 1
  ymin = 0
  ymax = 1
  zmin = 0
  zmax = 1
  elem_type = HEX8
[]

[Variables]
  active = 'u'

  [./u]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[Functions] #Added so that we can use the Postprocessor
  active = 'solution'

  [./solution]
    type = ParsedFunction
    expression = sin(a*x*y*z*t)
    symbol_names = 'a'
    symbol_values = '3.141592653589793'
  [../]
[]

[AuxVariables] #We added nodal AuxVariables
  active = 'nodal_aux'

  [./nodal_aux]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[Kernels]

  active = 'diff implicit conv forcing reaction'

  [./diff]
    type = MMSDiffusion
    variable = u
  [../]

  [./implicit] #We got from MOOSE kernels
    type = MMSImplicitEuler
    variable = u
  [../]

  [./conv] #We created our own convection kernel
    type = MMSConvection
    variable = u
    x = -1
    y = 2
    z = -3
  [../]

  [./forcing] #We created our own forcing kernel
    type = MMSForcing
    variable = u
  [../]

  [./reaction] #We got from MOOSE kernels
    type = MMSReaction
    variable = u
  [../]
[]

[AuxKernels] #We created our own AuxKernel
  active = 'ConstantAux'

  [./ConstantAux]
    type = MMSConstantAux
    variable = nodal_aux
  [../]
[]

[BCs]
  active = 'all_u'

  [./all_u]
    type = MMSCoupledDirichletBC
    variable = u
    boundary = '0 1 2 3 4 5'
 #   value = sin(a*x*y*z*t)
  [../]
[]

[Executioner]
  type = Transient
  dt = .1
  num_steps = 5

  solve_type = 'PJFNK'
[]

[Postprocessors]
  active = 'l2_error dofs'

  [./l2_error]
    type = ElementL2Error
    variable = u
    function = solution
    execute_on = 'initial timestep_end'
  [../]

  [./dofs]
    type = NumDOFs
    execute_on = 'initial timestep_end'
  [../]
[]


[Outputs]
  file_base = 3_d_postprocessor_out
  csv = true
[]
