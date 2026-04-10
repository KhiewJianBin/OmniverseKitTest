# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import omni.ext
import omni.usd

import omni.ui as ui

import omni.kit.commands
import omni.kit.app
import omni.kit.raycast.query
import omni.kit.viewport.utility

from pxr import UsdGeom, Gf, Sdf
import random
import omni.appwindow

from omni.kit.menu.utils import MenuItemDescription

import carb
import carb.input



# Any class derived from `omni.ext.IExt` in the top level module (defined in
# `python.modules` of `extension.toml`) will be instantiated when the extension
# gets enabled, and `on_startup(ext_id)` will be called. Later when the
# extension gets disabled on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    """This extension manages a simple counter UI."""
    # ext_id is the current extension id. It can be used with the extension
    # manager to query additional information, like where this extension is
    # located on the filesystem.
    def on_startup(self, _ext_id):
        print("[tutorial.editor.random_prim_ui] Extension startup")
        # add actions
        self._ext_name =  omni.ext.get_extension_name(_ext_id)
        self.register_actions(self._ext_name)

        # add menu item
        self._menu_list = [
            MenuItemDescription(
                    name="Random Prim UI",
                    onclick_action=(self._ext_name, "random_prim_ui"),
            )
        ]

        omni.kit.menu.utils.add_menu_items(self._menu_list, "Tutorial Menu")

        self._count = 0
        self._window = None

    def on_shutdown(self):
        print("[tutorial.editor.random_prim_ui] Extension shutdown")
        self.deregister_actions(self._ext_name)

        if self._window:
            self._window.destroy()

    def create_window(self):
        self._window = ui.Window("Random Prim UI", width=300, height=150)

        with self._window.frame:
            with ui.VStack():
                label = ui.Label("", height=ui.Percent(15), style={"alignment": ui.Alignment.CENTER})

                def on_click():
                    step = self._step_size_model.as_int
                    self._count += step
                    label.text = f"count: {self._count}"
                    scatter_cones(step)

                def on_reset():
                    self._count = 0
                    label.text = "empty"
                    clear_cones()


                with ui.HStack():
                    ui.Button("Add", clicked_fn=on_click)
                    ui.Button("Reset", clicked_fn=on_reset)


                with ui.HStack(height=0):
                    ui.Label("Step Size", style={"alignment": ui.Alignment.RIGHT_CENTER})
                    ui.Spacer(width=8)
                    self._step_size_model = ui.IntDrag(min=1, max=10).model
                    self._step_size_model.set_value(1)

    def register_actions(self, _ext_name: str):
        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "My Actions"

        action_registry.register_action(
            _ext_name,
            "random_prim_ui",
            lambda: self.create_window(),
            display_name="Register Random Prim UI",
            description="Register the Random Prim UI, which enables the user to randomly generate cones and delete all cones.",
            tag=actions_tag,
        )

    def deregister_actions(self, _ext_name: str):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(_ext_name)


def scatter_cones(quantity: int):

    usd_context = omni.usd.get_context()
    stage = usd_context.get_stage()

    for _ in range(quantity):
        prim_path = omni.usd.get_stage_next_free_path(
            stage,
            str(stage.GetPseudoRoot().GetPath().AppendPath("Cone")),
            False
        )

        omni.kit.commands.execute(
            "CreatePrimCommand",
            prim_path=prim_path,
            prim_type="Cone",
            attributes={"radius": 50, "height": 100},
            select_new_prim=True,
        )

        bound = 500
        rand_x = random.uniform(-bound, bound)
        rand_z = random.uniform(-bound, bound)

        translation = (rand_x, 0, rand_z)
        omni.kit.commands.execute(
            "TransformPrimSRT",
            path=prim_path,
            new_translation=translation,
        )

def clear_cones():
    usd_context = omni.usd.get_context()
    stage = usd_context.get_stage()

    # Empty list to hold paths of matching primitives
    matched_cones = []

    # Iterate over all prims in the stage
    for prim in stage.TraverseAll():
        # Check if the prim's name starts with the pattern
        if prim.GetName().startswith("Cone"):
            matched_cones.append(prim.GetPath())

    # Delete all the Cone prims
    omni.kit.commands.execute("DeletePrims", paths=matched_cones)


async def SpawnOnMouse():
    x, y = get_mouse_position_normalized()
    mousePos = get_mouse_position_normalized()

    hit_pos = await raycast_from_mouse(x, y, omni.kit.viewport.utility.get_active_viewport())

    print (mousePos)

    if hit_pos:
        print(f"Hit at: {hit_pos}")

        stage = omni.usd.get_context().get_stage()

        prim_path = omni.usd.get_stage_next_free_path(
            stage,
            str(stage.GetPseudoRoot().GetPath().AppendPath("Cone")),
            False
        )

        omni.kit.commands.execute(
            "CreatePrimCommand",
            prim_path=prim_path,
            prim_type="Cone",
            attributes={"radius": 50, "height": 100},
            select_new_prim=True,
        )
        omni.kit.commands.execute(
            "TransformPrimSRT",
            path=prim_path,
            new_translation=hit_pos,
        )

    else:
        print("No hit")

def get_mouse_position_normalized():
    
    app_window = omni.appwindow.get_default_app_window()
    mouse = app_window.get_mouse()  # ← correct way

    input_iface = carb.input.acquire_input_interface()
    pos = input_iface.get_mouse_coords_normalized(mouse)
    return pos.x, pos.y

async def raycast_from_mouse(mouse_norm_x: float, mouse_norm_y: float, viewport_api) -> Gf.Vec3d | None:
    """
    Fires an RTX raycast from normalised mouse coords [0..1] and returns
    the world-space hit position, or None if nothing was hit.

    Args:
        mouse_norm_x:  Normalised mouse X in [0, 1] (left → right)
        mouse_norm_y:  Normalised mouse Y in [0, 1] (top → bottom)
        viewport_api:  Active viewport API instance

    Returns:
        Gf.Vec3d world position of the hit, or None.
    """
    vp_w, vp_h = viewport_api.resolution

    # Normalised mouse → NDC [-1, 1] (Y flipped for OpenGL convention)
    ndc_x =  (2.0 * mouse_norm_x) - 1.0
    ndc_y = -((2.0 * mouse_norm_y) - 1.0)

    # Unproject near and far NDC points into world space
    ndc_to_world: Gf.Matrix4d = viewport_api.ndc_to_world
    near_world = ndc_to_world.Transform(Gf.Vec3d(ndc_x, ndc_y, -1.0))
    far_world  = ndc_to_world.Transform(Gf.Vec3d(ndc_x, ndc_y,  1.0))

    ray_origin = near_world
    ray_dir    = (far_world - near_world).GetNormalized()

    # Fire the RTX raycast (synchronous result via mutable container trick)
    result_container = [None]

    def _cb(ray, result):
        if result.valid:
            result_container[0] = Gf.Vec3d(*result.hit_position)

    raycast_iface = omni.kit.raycast.query.acquire_raycast_query_interface()
    ray = omni.kit.raycast.query.Ray(
        (float(ray_origin[0]), float(ray_origin[1]), float(ray_origin[2])),
        (float(ray_dir[0]),    float(ray_dir[1]),    float(ray_dir[2])),
    )
    raycast_iface.submit_raycast_query(ray, _cb)

    await omni.kit.app.get_app().next_update_async()

    return result_container[0]  # Gf.Vec3d or None

async def raycast_from_mouse2(mouse_norm_x: float, mouse_norm_y: float, viewport_api) -> Gf.Vec3d | None:

    vp_w, vp_h = viewport_api.resolution

    # Normalised mouse → NDC [-1, 1] (Y flipped for OpenGL convention)
    ndc_x =  (2.0 * mouse_norm_x) - 1.0
    ndc_y = -((2.0 * mouse_norm_y) - 1.0)

    # Unproject near and far NDC points into world space
    ndc_to_world: Gf.Matrix4d = viewport_api.ndc_to_world
    near_world = ndc_to_world.Transform(Gf.Vec3d(ndc_x, ndc_y, -1.0))
    far_world  = ndc_to_world.Transform(Gf.Vec3d(ndc_x, ndc_y,  1.0))

    ray_origin = near_world
    ray_dir    = (far_world - near_world).GetNormalized()

    raycast = omni.kit.raycast.query.acquire_raycast_query_interface()  
    ray = omni.kit.raycast.query.Ray(
        (float(ray_origin[0]), float(ray_origin[1]), float(ray_origin[2])),
        (float(ray_dir[0]),    float(ray_dir[1]),    float(ray_dir[2])),
    )

    seq_id = raycast.add_raycast_sequence()
    result = raycast.submit_ray_to_raycast_sequence(seq_id, ray)
    
    #return await poll_for_result() 

    # poll until result is ready
    result_pos = None
    for _ in range(10):  # max 10 frames wait
        await omni.kit.app.get_app().next_update_async()
        error, seq_ray, result = raycast.get_latest_result_from_raycast_sequence(seq_id)
        if error == omni.kit.raycast.query.Result.SUCCESS:
            if result.valid:
                result_pos = Gf.Vec3d(*result.hit_position)
            break

    raycast.remove_raycast_sequence(seq_id)
    return result_pos