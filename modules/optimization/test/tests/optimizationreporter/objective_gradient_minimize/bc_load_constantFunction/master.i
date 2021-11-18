# This tests that a function NeumannBC with a constant value
# parsed function can be parameterized.

[StochasticTools]
[]

[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 20
  xmax = 1
  ymax = 2
  bias_x = 1.1
  bias_y = 1.1
[]


[OptimizationReporter]
  type = ObjectiveGradientMinimize
  parameter_names = 'p1 p2'
  num_values = '1 1'
  adjoint_data_name = 'adjoint'
[]

[Executioner]
  type = Optimize
  tao_solver = taolmvm
  petsc_options_iname = '-tao_gatol'# -tao_cg_delta_max'
  petsc_options_value = '1e-4'
  # petsc_options_iname = '-tao_fd_gradient -tao_fd_delta -tao_gatol'
  # petsc_options_value = 'true 0.0001 1e-4'
   # petsc_options_iname='-tao_max_it -tao_fd_test -tao_test_gradient -tao_fd_gradient -tao_fd_delta -tao_gatol'
   # petsc_options_value='3 true true false 0.0001 0.0001'
  # verbose = true
[]

[MultiApps]
  [forward]
    type = OptimizeFullSolveMultiApp
    input_files = forward.i
    execute_on = "FORWARD"
    clone_master_mesh = true
  []
  [adjoint]
    type = OptimizeFullSolveMultiApp
    input_files = adjoint.i
    execute_on = "ADJOINT"
    clone_master_mesh = true
  []
[]

[Transfers]
  [toforward]
    type = OptimizationParameterTransfer
    multi_app = forward
    value_names = 'p1 p2'
    parameters = 'Postprocessors/p1/value Postprocessors/p2/value'
    to_control = parameterReceiver
  []
  [fromforward]
    type = MultiAppReporterTransfer
    multi_app = forward
    direction = from_multiapp
    from_reporters = 'data_pt/temperature_difference data_pt/temperature'
    to_reporters = 'OptimizationReporter/misfit receiver/measured'
  []
  [toadjoint_misfit]
    type = MultiAppReporterTransfer
    multi_app = adjoint
    direction = to_multiapp
    from_reporters = 'OptimizationReporter/misfit'
    to_reporters = 'point_source/value'
  []
  [fromadjoint]
    type = MultiAppReporterTransfer
    multi_app = adjoint
    direction = from_multiapp
    from_reporters = 'adjoint_bc/adjoint_bc'
    to_reporters = 'OptimizationReporter/adjoint'
  []
[]

[Reporters]
  [receiver]
    type = ConstantReporter
    real_vector_names = measured
    real_vector_values = '0 0 0 0'
   []
[]

[Outputs]
  csv=true
[]
