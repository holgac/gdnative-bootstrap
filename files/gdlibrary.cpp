#include <Godot.hpp>
#include <Spatial.hpp>
#include <Singleton.h>
#include "Game.h"

extern "C" void GDN_EXPORT godot_gdnative_init(godot_gdnative_init_options *o) {
  godot::Godot::gdnative_init(o);
  if (!o->in_editor) {
    auto& game = hol::Singleton<Game>::create();
    game.init();
  }
}

extern "C" void GDN_EXPORT godot_gdnative_terminate(godot_gdnative_terminate_options *o) {
  if (!o->in_editor) {
    hol::Singleton<Game>::get().deinit();
    hol::Singleton<Game>::reset();
  }
  godot::Godot::gdnative_terminate(o);
}

extern "C" void GDN_EXPORT godot_nativescript_init(void *handle) {
  godot::Godot::nativescript_init(handle);
  hol::Singleton<Game>::get().registerControllers();
}
