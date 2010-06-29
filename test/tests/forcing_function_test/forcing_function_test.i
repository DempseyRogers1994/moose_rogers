[Mesh]
  dim = 2
  file = square.e
  uniform_refine = 4
[]

[Variables]
  active = 'u'

  [./u]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[Kernels]
  active = 'diff forcing'

  [./diff]
    type = Diffusion
    variable = u
  [../]

  [./forcing]
    type = UserForcingFunction
    variable = u
    function = alpha*alpha*pi*pi*sin(alpha*pi*x)
    vars = 'alpha'
    vals = '16'
  [../]
[]

[BCs]
  active = 'left right'

  [./left]
    type = DirichletBC
    variable = u
    boundary = '1'
    value = 0
  [../]

  [./right]
    type = DirichletBC
    variable = u
    boundary = '2'
    value = 0
  [../]
[]

[Materials]
  active = empty

  [./empty]
    type = EmptyMaterial
    block = 1
  [../]
[]

[Executioner]
  type = Steady
  perf_log = true
[]

[Output]
  file_base = out
  interval = 1
  exodus = true
[]
