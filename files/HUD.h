#pragma once
#include <Control.hpp>
#include <array>
#include <vector>

namespace godot {
  class HUD : public Control {
    GODOT_CLASS(HUD, Control)

  public:
    static void _register_methods() {
      register_method("_enter_tree", &HUD::_enter_tree);
      register_method("_exit_tree", &HUD::_exit_tree);
      register_method("_ready", &HUD::_ready);
      register_method("_process", &HUD::_process);
      register_method("_input", &HUD::_input);
    }

    void _init() {}

    void _enter_tree() {}

    void _exit_tree() {}

    void _ready() {}

    void _process(float delta) {}

    void _input(const Ref<InputEvent> event) {}

  private:
  };
}


