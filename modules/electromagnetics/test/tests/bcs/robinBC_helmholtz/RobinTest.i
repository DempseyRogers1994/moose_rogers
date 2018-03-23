# problem: -(ku')' - c^2 * u' = 0 , 0 < x < L, u: R -> C
# u(x=0) = g0 , u'(x = L) = 2jcf(L)*exp(jcLf(L)) - jcf(L)u(x = L)
# c = a + jb , k = d + jh

[GlobalParams]
  length = 1
  coeff_real = 15
  coeff_imag = 7
[]

[Mesh]
  type = GeneratedMesh
  dim = 1
  xmin = 0
  xmax = 1
  nx = 100
[]

[Variables]
  [./u_real]
    order = FIRST
    family = LAGRANGE
  [../]
  [./u_imag]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[Functions]
  [./ASquaredMinusBSquared]
    type = ParsedFunction
    value = '15*15 - 7*7'
  [../]
  [./2TimesAB]
    type = ParsedFunction
    value = '2*15*7'
  [../]
  [./cos]
    type = ParsedFunction
    value = 'cos(0.5)'
  [../]
[]

[Kernels]
  [./laplacian_real]
    type = CoeffDiffusion
    coefficient = 1
    variable = u_real
  [../]
  [./coupledLaplacian_real]
    type = CoupledCoeffDiffusion
    coefficient = 0
    sign = -1.0
    coupled_field = u_imag
    variable = u_real
  [../]
  [./kSquaredEpsField_real]
    type = CoeffField
    func = ASquaredMinusBSquared
    variable = u_real
  [../]
  [./coupledField_real]
    type = CoupledCoeffField
    coupled_field = u_imag
    func = 2TimesAB
    sign = 1.0
    variable = u_real
  [../]
  [./laplacian_imag]
    type = CoeffDiffusion
    coefficient = 1
    variable = u_imag
  [../]
  [./coupledLaplacian_imag]
    type = CoupledCoeffDiffusion
    coefficient = 0
    sign = 1.0
    coupled_field = u_real
    variable = u_imag
  [../]
  [./kSquaredEpsField_imag]
    type = CoeffField
    func = ASquaredMinusBSquared
    variable = u_imag
  [../]
  [./coupledField_imag]
    type = CoupledCoeffField
    coupled_field = u_real
    func = 2TimesAB
    sign = -1.0
    variable = u_imag
  [../]
[]

[BCs]
  [./left_real]
    type = DirichletBC
    value = 0
    boundary = left
    variable = u_real
  [../]
  [./left_imag]
    type = DirichletBC
    value = 1
    boundary = left
    variable = u_imag
  [../]
  [./right_real]
    type = RobinReflectionBC
    func_real = cos
    boundary = right
    component = real
    variable = u_real
    coupled_variable = u_imag
  [../]
  [./right_imag]
    type = RobinReflectionBC
    func_real = cos
    boundary = right
    component = imaginary
    variable = u_imag
    coupled_variable = u_real
  [../]
[]

[Executioner]
  type = Steady
  solve_type = 'PJFNK'
[]

[Outputs]
  exodus = true
[]
