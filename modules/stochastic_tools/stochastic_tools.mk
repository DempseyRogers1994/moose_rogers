app_non_unity_dirs = %src/surrogates %src/utils

# Looking for the installation (maybe it is in the default location)
ifeq ($(TORCH_DIR),)
  TORCH_DIR ?= $(MOOSE_DIR)/framework/contrib/libtorch
endif

ifneq ($(TORCH_DIR),)
	UNAME_S := $(shell uname -s)
	LIBTORCH_LIB := libtorch.so
  ifeq ($(UNAME_S),Darwin)
    LIBTORCH_LIB := libtorch.dylib
  endif

  ifneq ($(wildcard $(TORCH_DIR)/lib/$(LIBTORCH_LIB)),)
    # Enabling parts that have pytorch dependencies
    libmesh_CXXFLAGS += -DTORCH_ENABLED

    # Adding the include directories, we use -isystem to silence the warning coming from
		# libtorch (which would cause errors in the testing phase)
    libmesh_CXXFLAGS += -isystem $(TORCH_DIR)/include/torch/csrc/api/include
    libmesh_CXXFLAGS += -isystem $(TORCH_DIR)/include

    # Dynamically linking with the available pytorch library
    libmesh_LDFLAGS += -Wl,-rpath,$(TORCH_DIR)/lib
    libmesh_LDFLAGS += -L$(TORCH_DIR)/lib -ltorch
  else
    $(info ERROR! Could not find any dynamic libraries of libtorch.)
    $(info Please check the following directory $(TORCH_DIR)/lib)
    $(info Build will proceed without the compilation of libtorch-related parts.)
  endif
else
    $(info ERROR! Could not find active libtorch installation.)
    $(info Try to run $(APPLICATION_DIR)/scripts/setup_pytorch.sh before calling make!)
    $(info Build will proceed without the compilation of libtorch-related parts.)
endif
