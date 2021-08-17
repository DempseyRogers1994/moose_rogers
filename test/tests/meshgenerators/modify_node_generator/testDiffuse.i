[Mesh]
  [./eg]
    type = CartesianMeshGenerator
    dim = 3
    dx = '1'
    dy = '1'
    dz = '1'
    ix = '4'
    iy = '4'
    iz = '4'
    subdomain_id = '0'
  []
  [modifyNode]
    type = ModifyNodeGenerator
    input = eg
    node_id = '0 1 2'
    new_position = '0 0 0
                    0.15 0 0.15
                    0.1stash5 0 0'
  []
[]

[Variables]
  [u]
  []
[]

[Kernels]
  [diff]
    type = Diffusion
    variable = u
  []
[]

[BCs]
  [left]
    type = DirichletBC
    variable = u
    boundary = left
    value = 0
  []
  [right]
    type = DirichletBC
    variable = u
    boundary = right
    value = 1
  []
[]

[Executioner]
  type = Steady
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  exodus = true
[]
