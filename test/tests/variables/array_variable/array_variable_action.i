[Mesh]
  [gmg]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 3
    ny = 3
  []
[]

[Testing/LotsOfDiffusion/lots]
  number = 1
  array = true
[]

[Executioner]
  type = Steady
[]

[Outputs]
  exodus = true
[]
