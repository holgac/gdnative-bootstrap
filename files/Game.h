#include "HUD.h"

class Game {
public:
  Game() {
  }

  void init() {
  }

  void deinit() {
  }

  void registerControllers() {
      godot::register_class<godot::HUD>();
  }
};